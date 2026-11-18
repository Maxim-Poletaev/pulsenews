from django.core.paginator import Paginator


class ElidedPaginator(Paginator):
    """
    Пагинатор, который отдаёт «окно» страниц вокруг текущей:
    1 … 4 5 [6] 7 8 … 20
    """
    def get_elided_page_range(self, number, on_each_side=2, on_ends=1):
        return super().get_elided_page_range(
            number, on_each_side=on_each_side, on_ends=on_ends
        )