

def get_page_list(total, index_id):
    """构造页码列表"""
    # 进行分页判断
    if total <= 5:
        page_list = range(1, total+1)
    elif index_id <= 2:
        page_list = range(1, index_id+1)
    elif index_id >= total-1:
        page_list = range(total-4, total+1)
    else:
        page_list = range(index_id-2, index_id+3)

    return page_list