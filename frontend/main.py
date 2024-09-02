import os
from dotenv import load_dotenv
from typing import List
import uuid
import requests
import streamlit as st

from utils import *

load_dotenv()

st.title('HCMUT FOL REASONING SYSTEM')

# main_columns = st.columns((15, 5))

st.header('Premises')
st.text_area('Enter your premises here:', height=200, key='premises', value='∀x,(Hinh_Vuong(x)→ Chu_Nhat(x))')
st.caption('Premises are separated by new lines')

predicate_values = get_predicate_dict(st.session_state.get('premises', ''))

if "facts" not in st.session_state:
    st.session_state["facts"] = []

facts_collection = []

if "queries" not in st.session_state:
    st.session_state["queries"] = []

queries_collection = []

def add_fact():
        fact_id = str(uuid.uuid4())
        st.session_state["facts"].append(fact_id)

def remove_fact(fact_id):
    st.session_state["facts"].remove(fact_id)

def generate_fact(fact_id):
    fact_container = st.empty()
    fact_columns = fact_container.columns((2, 3, 2, 1), vertical_alignment='center')
    predicate = fact_columns[0].selectbox('Predicate', predicate_values, key=f"predicate_{fact_id}")
    fact_value = fact_columns[1].text_input('Entity Value(s)', key=f"fact_name_{fact_id}")
    fact_gt_value = fact_columns[2].selectbox('Entity Truth Value', ['TRUE', 'FALSE', 'UNKNOWN'], key=f"fact_value_{fact_id}")
    
    fact_columns[3].write('')
    fact_columns[3].write('')
    fact_columns[3].button('x', key=f"del_{fact_id}", on_click=remove_fact, args=[fact_id])
    
    return {
        'fact_id': fact_id,
        'predicate': predicate,
        'fact_value': fact_value,
        'fact_gt_value': fact_gt_value
    }

def add_query():
    query_id = str(uuid.uuid4())
    st.session_state["queries"].append(query_id)

def remove_query(query_id):
    st.session_state["queries"].remove(query_id)

def search_predicates(searchterm: str) -> List[any]:
    # search similar item in a list
    searchterm = searchterm.lower()
    return [predicate for predicate in predicate_values if searchterm in predicate.lower()] if searchterm else []

def generate_query(query_id):
    query_container = st.empty()
    query_columns = query_container.columns((3, 3, 1), vertical_alignment='center')

    query_stmt = query_columns[0].text_input('Query Statement', key=f"query_stmt_{query_id}")
    query_value = query_columns[1].text_input('Value', key=f"query_{query_id}")
    
    query_columns[2].write('')
    query_columns[2].write('')
    query_columns[2].button('x', key=f"del_{query_id}", on_click=remove_query, args=[query_id])
    
    return {
        'query_id': query_id,
        'query_stmt': query_stmt,
        'query_value': query_value
    }

if len(predicate_values) > 0:
    st.header('Facts')
    for fact in st.session_state["facts"]:
        fact_data = generate_fact(fact)
        facts_collection.append(fact_data)

    st.button("Add Fact", on_click=add_fact)

    st.header('Queries')
    for query in st.session_state["queries"]:
        query_data = generate_query(query)
        queries_collection.append(query_data)

    st.button("Add Query", on_click=add_query)

run_btn = st.button('Run', type='primary')

if run_btn:
    st.header('Results')

    reasoning_url = os.getenv('BASE_URL') + '/reasoning-lnn-explanation'

    expressions = st.session_state.get('premises', '').split('\n')
    
    if len(expressions) == 1 and expressions[0] == '':
        st.error('No premises found')
        st.stop()

    formatted_facts = dict()
    for fact in facts_collection:
        if fact['predicate'] not in formatted_facts:
            formatted_facts[fact['predicate']] = dict()
        formatted_facts[fact['predicate']][fact['fact_value']] = fact['fact_gt_value']

    formatted_queries = dict()
    for query in queries_collection:
        formatted_queries[query['query_stmt']] = query['query_value']

    results = requests.post(
        reasoning_url,
        json={
            'expression': expressions,
            'facts': formatted_facts,
            'question': formatted_queries
        }
    ).json()

    st.code(results, language='json', wrap_lines=True)
    


    
