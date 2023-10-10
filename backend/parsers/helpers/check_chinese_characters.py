def check_chinese_characters(char):
    if u'\u4e00' <= char <= u'\u9fff':
        return True
    return False