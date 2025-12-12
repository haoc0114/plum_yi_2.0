import streamlit as st
import datetime
from cnlunardate import cnlunardate
import random
import numpy as np
import pandas as pd
import time
from google import genai
# import google.generativeai as genai
gen_model="gemini-2.5-flash"

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("找不到 API Key，請檢查 secrets 設定。")
    st.stop()

client = genai.Client(api_key=api_key)

# -----------------------------------------------------------
tz = datetime.timezone(datetime.timedelta(hours=+8))   # 將時區固定在台灣
Stems = ['癸', '甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬']
Branches = ['亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌']
num2tri = {0: '000', 1: '111', 2: '110', 3: '101',
           4: '100', 5: '011', 6: '010', 7: '001'}
tri2num = {'000': 0, '111': 1, '110': 2, '101': 3,
           '100': 4, '011': 5, '010': 6, '001': 7}
Trigram = ['坤', '乾', '兌', '離', '震', '巽', '坎', '艮']
Trigram_sign = ['☷', '☰', '☱', '☲', '☳', '☴', '☵', '☶']
Hexagram = np.array([
    [2, 11, 19, 36, 24, 46, 7, 15],
    [12, 1, 10, 13, 25, 44, 6, 33],
    [45, 43, 58, 49, 17, 28, 47, 31],
    [35, 14, 38, 30, 21, 50, 64, 56],
    [16, 34, 54, 55, 51, 32, 40, 62],
    [20, 9, 61, 37, 42, 57, 59, 53],
    [8, 5, 60, 63, 3, 48, 29, 39],
    [23, 26, 41, 22, 27, 18, 4, 52]])
Hexagram_sign = np.array([
    ['䷁', '䷊', '䷒', '䷣', '䷗', '䷭', '䷆', '䷎'],
    ['䷋', '䷀', '䷉', '䷌', '䷘', '䷫', '䷅', '䷠'],
    ['䷬', '䷪', '䷹', '䷰', '䷐', '䷛', '䷮', '䷞'],
    ['䷢', '䷍', '䷥', '䷝', '䷔', '䷱', '䷿', '䷷'],
    ['䷏', '䷡', '䷵', '䷶', '䷲', '䷟', '䷧', '䷽'],
    ['䷓', '䷈', '䷼', '䷤', '䷩', '䷸', '䷺', '䷴'],
    ['䷇', '䷄', '䷻', '䷾', '䷂', '䷯', '䷜', '䷦'],
    ['䷖', '䷙', '䷨', '䷕', '䷚', '䷑', '䷃', '䷳']])
Hexagram_name = np.array([
    ['坤為地', '地天泰', '地澤臨', '地火明夷', '地雷復', '地風升', '地水師', '地山謙'],
    ['天地否', '乾為天', '天澤履', '天火同人', '天雷无妄', '天風姤', '天水訟', '天山遯'],
    ['澤地萃', '澤天夬', '兌為澤', '澤火革', '澤雷隨', '澤風大過', '澤水困', '澤山咸'],
    ['火地晉', '火天大有', '火澤睽', '離為火', '火雷噬嗑', '火風鼎', '火水未濟', '火山旅'],
    ['雷地豫', '雷天大壯', '雷澤歸妹', '雷火豐', '震為雷', '雷風恒', '雷水解', '雷山小過'],
    ['風地觀', '風天小畜', '風澤中孚', '風火家人', '風雷益', '巽為風', '風水渙', '風山漸'],
    ['水地比', '水天需', '水澤節', '水火既濟', '水雷屯', '水風井', '坎為水', '水山蹇'],
    ['山地剝', '山天大畜', '山澤損', '山火賁', '山雷頤', '山風蠱', '山水蒙', '艮為山']])


def gen_hexagram(x1, x2, x3):
    # 取出本卦及變卦，x1為上卦，x2為下卦，x3為動爻
    Original = Hexagram[x1][x2]
    Original_sign = Hexagram_sign[x1][x2]
    Original_name = Hexagram_name[x1][x2]
    sign_all = num2tri[x2] + num2tri[x1]
    m1 = tri2num[sign_all[2:5]]
    m2 = tri2num[sign_all[1:4]]
    Mutual = Hexagram[m1][m2]
    Mutual_sign = Hexagram_sign[m1][m2]
    Mutual_name = Hexagram_name[m1][m2]

    if x3 < 4:
        relation = ['體', '用']
        rr = 1
        temp = num2tri[x2]
        temp = list(temp)
        temp[x3-1] = str(abs(int(temp[x3-1])-1))
        tri = ''.join(temp)
        x2n = tri2num[tri]
        x1n = x1
        Future = Hexagram[x1n][x2n]
        Future_sign = Hexagram_sign[x1n][x2n]
        Future_name = Hexagram_name[x1n][x2n]
    else:
        relation = ['用', '體']
        rr =2
        temp = num2tri[x1]
        temp = list(temp)
        temp[x3-4] = str(abs(int(temp[x3-4])-1))
        tri = ''.join(temp)
        x1n = tri2num[tri]
        x2n = x2
        Future = Hexagram[x1n][x2n]
        Future_sign = Hexagram_sign[x1n][x2n]
        Future_name = Hexagram_name[x1n][x2n]

    link_1 = '[本卦解](https://www.eee-learning.com/book/neweee%02d' % Original+')'
    link_3 = '[互卦解](https://www.eee-learning.com/book/neweee%02d' % Mutual+')'
    link_2 = '[變卦解](https://www.eee-learning.com/book/neweee%02d' % Future+')'

    df2 = pd.DataFrame({'本卦': [Trigram_sign[x1]+Trigram[x1], Trigram_sign[x2]+Trigram[x2]],
                        '互卦': [Trigram_sign[m1]+Trigram[m1], Trigram_sign[m2]+Trigram[m2]],
                        '變卦': [Trigram_sign[x1n]+Trigram[x1n], Trigram_sign[x2n]+Trigram[x2n]]}, relation)
    if rr == 1:
        input_prompt = '你是一個精通梅花易數的占卜師，會從本卦的卦意並參考本卦的體卦和用卦的生剋及卦象關係去判斷當下，從互卦的卦意並參考互卦的體卦和用卦的生剋及卦象關係去判斷過程，從變卦的卦意並參考變卦的體卦和用卦的生剋及卦象關係去判斷結果，我想問的問題是'+question+'得到下面結果：'+'本卦：'+Original_name+',其中體卦為'+Trigram[x1]+',用卦為'+Trigram[x2]+',互卦：' +Mutual_name+',其中體卦為'+Trigram[m1]+',用卦為'+Trigram[m2]+',變卦：'+Future_name+',其中體卦為'+Trigram[x1n]+',用卦為'+Trigram[x2n]+'請認真查證卦意、體卦和用卦的生剋關係及卦象關係後幫我解卦'

    else:
        input_prompt = '你是一個精通梅花易數的占卜師，會從本卦的卦意並參考本卦的體卦和用卦的生剋及卦象關係去判斷當下，從互卦的卦意並參考互卦的體卦和用卦的生剋及卦象關係去判斷過程，從變卦的卦意並參考變卦的體卦和用卦的生剋及卦象關係去判斷結果，我想問的問題是'+question+'得到下面結果：'+'本卦：'+Original_name+',其中體卦為'+Trigram[x2]+',用卦為'+Trigram[x1]+',互卦：' +Mutual_name+',其中體卦為'+Trigram[m2]+',用卦為'+Trigram[m1]+',變卦：'+Future_name+',其中體卦為'+Trigram[x2n]+',用卦為'+Trigram[x1n]+'請認真查證卦意、體卦和用卦的生剋關係及卦象關係後幫我解卦'
        
    if AI_exp == 'AI解卦':
        message_placeholder = st.empty()
        message_placeholder.text("⚡ 正在與天地連線解卦中，請稍候...")

        try:
            response = client.models.generate_content_stream(
            model=gen_model,
            contents=input_prompt)

            def stream_parser(response):
                for chunk in response:
                    # Google API 有時會回傳空或是被擋下的內容，需做檢查
                    if chunk.text:
                        yield chunk.text
            message_placeholder.write_stream(stream_parser(response))
        
            # st.write(response.text)

            st.markdown(link_1+';   '+link_3+';   '+link_2, unsafe_allow_html=True)
            st.table(df2)
            st.header('AI咒語如下，可貼到喜歡的AI解卦')
            if rr == 1:
                st.code(input_prompt)
            #     st.code('''1你是一個精通梅花易數的占卜師，
            # 會從本卦的卦意並參考本卦的體用生剋及卦象關係去判斷當下，
            # 從互卦的卦意並參考互卦的體用生剋及卦象關係去判斷過程，
            # 從變卦的卦意並參考變卦的體用生剋及卦象關係去判斷結果，\n'''+
            #                 '我想問的問題是'+question+'得到下面結果：\n'+
            #                 '本卦：'+Original_name+',其中體卦為'+Trigram[x2]+',用卦為'+Trigram[x1]+
            #                 '\n互卦：' +Mutual_name+',其中體卦為'+Trigram[m2]+',用卦為'+Trigram[m1]+
            #                 '\n變卦：'+Future_name+',其中體卦為'+Trigram[x2n]+',用卦為'+Trigram[x1n]+
            #                 '\n請認真查證卦意、體用生剋關係及卦象關係後幫我解卦')
            else:
                st.code(input_prompt)
            #     st.code('''2你是一個精通梅花易數的占卜師，
            # 會從本卦的卦意並參考本卦的體用生剋及卦象關係去判斷當下，
            # 從互卦的卦意並參考互卦的體用生剋及卦象關係去判斷過程，
            # 從變卦的卦意並參考變卦的體用生剋及卦象關係去判斷結果，\n'''+
            #                 '我想問的問題是'+question+'得到下面結果：\n'+
            #                 '本卦：'+Original_name+',其中體卦為'+Trigram[x1]+',用卦為'+Trigram[x2]+
            #                 '\n互卦：' +Mutual_name+',其中體卦為'+Trigram[m1]+',用卦為'+Trigram[m2]+
            #                 '\n變卦：'+Future_name+',其中體卦為'+Trigram[x1n]+',用卦為'+Trigram[x2n]+
            #                 '\n請認真查證卦意、體用生剋關係及卦象關係後幫我解卦')
            
        except Exception as e:
            message_placeholder.error(f"連線發生錯誤：{e}")
    else:
        st.header('本卦為第'+str(Original)+'卦'+Original_sign+Original_name)
        st.header('互卦為第'+str(Mutual)+'卦'+Mutual_sign+Mutual_name)
        st.header('變卦為第'+str(Future)+'卦'+Future_sign+Future_name)
        st.markdown(link_1+';   '+link_3+';   '+link_2, unsafe_allow_html=True)
        st.table(df2)
        st.header('AI咒語如下，可貼到喜歡的AI解卦')
        if rr == 1:
            st.code(input_prompt)
        else:
            st.code(input_prompt)
    

st.title('梅花易數占卜')
date_now = datetime.datetime.now(tz)
st.text(str(date_now.date()) + '   ' +
         str(date_now.hour) + ':' + str(date_now.minute))

date_l = cnlunardate.fromsolardate(date_now.date())   # 農曆日期
y1 = (date_l.year-3) % 10
y2 = (date_l.year-3) % 12
month_l = date_l.month
day_l = date_l.day
hour = int((date_now.hour+1)/2 % 12)+1
if hour == 12:
    hour = 0
st.text(Stems[y1]+Branches[y2] + '年' + str(month_l) +'月'+str(day_l)+'號' + Branches[hour] + '時')
st.header('不誠不占，不義不占，不疑不占')
question = st.text_input("請輸入想卜的事，寫詳細一點:")
method = st.selectbox('請選擇起卦方式，連續占卜不要用時間起卦', ['依當下時間起卦', '亂數起卦', '輸入數字起卦'])
AI_exp = st.radio('', ['AI解卦', '僅取卦'])

if method == '依當下時間起卦':
    s1 = (y2+month_l+day_l) % 8
    s2 = (y2+month_l+day_l+hour) % 8
    s3 = (y2+month_l+day_l+hour) % 6
    if (s3 == 0):
        s3 = 6
    if st.button('起卦'):
        if question == '':
            st.warning('請輸入問題')
            st.stop()
        else:
            up_sign = Trigram[s1]
            down_sign = Trigram[s2]
            alt = str(s3)
            gen_hexagram(s1, s2, s3)
elif method == '亂數起卦':
    n1 = random.randint(1, 72)
    n2 = random.randint(1, 72)
    s1 = n1 % 8
    s2 = n2 % 8
    s3 = (n1 + n2) % 6
    if (s3 == 0):
        s3 = 6
    if st.button('起卦'):
        if question == '':
            st.warning('請輸入問題')
            st.stop()
        else:
            up_sign = Trigram[s1]
            down_sign = Trigram[s2]
            alt = str(s3)
            gen_hexagram(s1, s2, s3)
else:
    temp = st.text_input('請輸入兩個整數，中間用空格分開')

    if st.button('起卦'):
        if temp == '':
            st.warning('請輸入兩個整數')
            st.stop()
        else:
            n1 = int(temp.split()[0])
            n2 = int(temp.split()[1])
            s1 = n1 % 8
            s2 = n2 % 8
            s3 = (n1 + n2) % 6
            if s3 == 0:
                s3 = 6
            if question == '':
                st.warning('請輸入問題')
                st.stop()
            else:
                up_sign = Trigram[s1]
                down_sign = Trigram[s2]
                alt = str(s3)
                gen_hexagram(s1, s2, s3)

