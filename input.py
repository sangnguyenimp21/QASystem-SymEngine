# Note:
# + predicate không được chứa số, Ví dụ: ThuocMuc3(x)
# + Phải có dấu ',' phía sau các biến, Ví dụ: ∀x,(...
# + Chỉ sử dụng dấu ngoặc tròn trong FOL
# + Nếu như có 2 lượng từ ∀ trở lên thì gộp thành 1 ∀, ví dụ: ∀x,hk

fol_expressions = [
    "∀x,(Hinh_Vuong(x)→ Chu_Nhat(x))",
    "∀x,(Chu_Nhat(x)→ Bon_Canh(x))",
    "∀x,(Bon_Canh(x)∧Cap_canh_song_song(x) → Hinh_thoi(x))",
]
facts = [("Bon_Canh", "S", "True"), ("Cap_canh_song_song", "S", "True")]
question = "Hinh_thoi"


def get_fol_expressions():
    return fol_expressions


def get_facts():
    return facts


def get_question():
    return question
