import pandas as pd
import re

# 3.3 Data Exploring and Processing
# 3.3.1 Data Information Exploring
# read the crawling orignial data file
all_sales_data = pd.read_csv('tmp/手机销售数据.csv', encoding='gbk')
after_sales_data = pd.read_csv('tmp/手机售后数据.csv', encoding='utf-8')
all_sales_data['商品编号']=all_sales_data['商品编号'].astype(str)
# Self define the analysis function to implement descriptive stats analysis and data missing analysis
def analysis(data):
    print('描述性统计分析结果为：\n', data.describe())
    print('各属性缺失值占比为：\n', 100*(data.isnull().sum() / len(data)))
# Cellphone sales data
print(analysis(all_sales_data))
# Cellphone after-sales data
print(analysis(after_sales_data))



# 3.3.2 Missed data processing
# Remove the missed data for store name, cellphone colore and memory
all_sales_data.dropna(axis=0, subset = ['店铺名称'], inplace=True)
after_sales_data.dropna(axis=0, subset = ['手机配色', '手机内存'], inplace=True)
# Fill the missing value of the CPU type, rear master pixel, the front master pixel, and the system attribute
null_data = all_sales_data.loc[((all_sales_data['CPU型号'].isnull() == True) | 
                                (all_sales_data['前摄主摄像素'].isnull() == True) |
                                (all_sales_data['后摄主摄像素'].isnull() == True)), 
                               '商品名称'].drop_duplicates()

for j in null_data:
    for i in ['CPU型号', '后摄主摄像素', '前摄主摄像素', '系统']:
        d = all_sales_data[all_sales_data['商品名称'] == j]
        g = d[d[i].isnull() == False]
        if len(g) != 0 :
            t = list(g[i])[0]
            all_sales_data.loc[((all_sales_data['商品名称'] == j) & (all_sales_data[i].isnull())), i] = t
        else :
            all_sales_data.loc[((all_sales_data['商品名称'] == j) & (all_sales_data[i].isnull())), i] = '其他'

# 3.3.3 Duplicate value processing
print('删除重复值前的手机销售数据维度：', all_sales_data.shape)
print('删除重复值前的手机售后数据维度：', after_sales_data.shape)

# Keep the first one and remove other duplicate data
all_sales_data = all_sales_data.drop_duplicates()
print('删除重复值后的手机销售数据维度：', all_sales_data.shape)
after_sales_data = after_sales_data.drop_duplicates()
print('删除重复值后的手机售后数据维度：', after_sales_data.shape)



# 3.3.4 Text processing
# Clear the text content of mobile phone brand and product name attributes in mobile phone sales data
# Selects other data information other than the parentheses themselves and their contents
all_sales_data['手机品牌'] = [i.split('（')[0] for i in all_sales_data['手机品牌']]
# Select non-[],5G,4G,new products, the phone itself and its associated other data information
all_sales_data['商品名称'] = [re.split('【.*】|5G.*|4G.*|新品.*|手机.*',i)[0] for i in all_sales_data['商品名称']]
# Modify other OS into 其他
all_sales_data['系统'] = all_sales_data['系统'].str.replace('其他OS', '其他')


# Clean the text content of the comment text attribute in the after-sales data of the mobile phone
# Delete the newline character
after_sales_data['评论文本'] = after_sales_data['评论文本'].str.replace('\n', '')
# Remove emoticons in html (beginning with &, middle with letter, end with ;), just processes the emojis in the text, does not delete the text
after_sales_data['评论文本'] = after_sales_data['评论文本'].str.replace('&[a-z]+;', '', regex=True)


# Clean the text content of the default praise in the after-sales data of the phone
after_sales_data = after_sales_data[after_sales_data['评论文本'] !='您没有填写内容，默认好评']

# Write out data
all_sales_data.to_csv('tmp/处理后的手机销售数据.csv', index=False, encoding='gbk')
after_sales_data.to_csv('tmp/处理后的手机售后数据.csv', index=False, encoding='utf-8')


