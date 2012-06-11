from items.models import Question, Answer

POINTSTABLE = {
        Question._meta.module_name: {-1: -2, 1: 5},
        Answer._meta.module_name: {-1: -2, 1: 10},
}
