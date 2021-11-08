import re


class date_regex:
    def __init__(self):
        self.date_pattern = r'[\d]{1,2}\/[\d]{1,2}\/[\d]{4}:'

    def set_replace_date(self, txt: str):
        dates = re.findall(self.date_pattern, txt)
        for date in dates:
            txt = txt.replace(date, "DATE_REPLACED:")
        return dates, txt

    def get_date_wise_content(self, dates: list, txt: str):
        section_with_date = {}
        x = re.split(self.date_pattern, txt)[1:]
        x[len(x)-1] = re.split("\n\n", x[len(x)-1])[0]
        for i in range(len(dates)):
            section_with_date[dates[i][:-1]] = x[i].strip().replace("\n", " ")
        return section_with_date

    def reset_replace_date(self, dates: list, txt: str):
        for date in dates:
            txt = txt.replace("DATE_REPLACED:", date, 1)
        return txt
