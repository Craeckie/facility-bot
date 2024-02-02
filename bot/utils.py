from bs4 import BeautifulSoup, Comment
import os
import requests
import datetime
import traceback
import pickle


def load_list(r):
    data = r.get('temp:list')
    if data:
        l = pickle.loads(data)
        return l
    else:
        return []


def parseMull(street, house_number):
    current_year = datetime.datetime.now().year
    urls = [os.environ.get(variable).format(year=year)
            for year in [current_year, current_year - 1, current_year - 2]
            for variable in ['TRASH_URL', 'TRASH_URL_ALT']]
    verify = os.environ.get('VERIFY_CERT', 'True').lower() in ('true', 't', 'y', 'yes', 'on', '1')
    url_alt = os.environ.get('TRASH_URL_WEBSITE') # in case of error
    # Check network tab for actual request
    form_data = {
        'strasse_n': street,
        'hausnr': house_number,
        'anzeigen': 'anzeigen'
    }
    msg = ''
    for url in urls:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Referer': url,
        }
        print("Trying with %s" % url)
        try:
            r = requests.post(url, headers=headers, data=form_data, verify=verify)
        except Exception as e:
            msg += 'Failed to open %s: %s' % (url, e)
            msg += traceback.format_exc() + '\n'
        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            comments = soup.find_all(string=lambda text: isinstance(text, Comment))
            [comment.extract() for comment in comments]
            cont = True
            content = soup.find('form', attrs={'name': 'a'})
            rows = content.find_all("div", attrs={"class": "row"}, recursive=False)
            header = rows[0]
            s_name_header = header.find("a")
            s = "<i>%s</i>\n\n" % s_name_header.text.strip()

            date_rows = rows[1:]
            for row in date_rows:
                header = True
                for entry in row.find_all('div'):
                    for content in entry.contents:
                        if content == 'Alle Angaben sind ohne Gewähr.':
                            cont = False
                            break
                        if content.name not in ['img', 'br', 'a']:
                            # print(content.name)
                            # print(type(content))
                            if content.name == 'b':
                                # print(content.text)
                                s += "<code>" + str(content.text) + "</code>" + '\n'
                            elif header:
                                s += f'\n<b>{content}</b>\n'
                                header = False
                            else:
                                # print(content)
                                s += content.strip() + '\n'
                    if not cont:
                        break
            s += '\n'
            msg = s.strip().replace('\n\n\n', '\n')
            return msg, True
        except Exception as e:
            msg += 'Failed to parse %s: %s' % (url, e)
            # msg += 'Html:\n%s\n\n' % (url, r.text)
            msg += traceback.format_exc() + '\n'
    if len(msg) > 3500:
        # to prevent errors when sending
        msg = msg[:3500] + "...\n\n"
    if url_alt:
        alt_msg = "<b>Please use the website instead</b>: %s" % url_alt
        msg = f'{alt_msg}\n\n{msg}{alt_msg}'
    return (msg, False)
