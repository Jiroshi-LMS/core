from apps.headless.common.utilities.Paginator import PAGINATION_SELECTOR

def pagination_selector(params: dict):
    pagination_param = params.get('pagination', '')
    return PAGINATION_SELECTOR.get(pagination_param, None)