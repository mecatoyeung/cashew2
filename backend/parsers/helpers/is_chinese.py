def is_chinese(s):
    return re.search(u'[\u4e00-\u9fff]', s)