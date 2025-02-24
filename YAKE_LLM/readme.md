## 文件说明

#### test.py

原 `gci.py` 文件



#### spark_extract 文件夹

和星火连接的文件包括 `SparkApi.py` 和 `SparkPythondemo.py`

##### SparkPythondemo.py

自定义的调用函数: 读取输入，提取LLM的输出等



#### PythonDemo(content) 文件夹

`SparkApi.py` 和 `SparkPythondemo.py` 的默认未修改官方示例文件



## 主要函数/修改

#### SparkApi.py

主要是参数有一点和默认的不一样

```python
def gen_params(appid, domain, question):
		...
            "chat": {
                "domain": domain,
                "temperature": 0.5,
                "max_tokens": 512,
                "top_k": 5,

                "auditing": "default"
            }
         ...
    return data
```



#### SparkPythondemo.py

##### 1. get_output

- 拼接prompt
- 生成循环：提取3次关键词
- 获得回答
- 过滤列表

##### 2. extract_keywords

- 匹配 “```json```" 包含的部分
- 回答可能有两种格式，所以匹配了两次
- 返回关键词列表或空列表

##### 3. 版本

主要是以下两个，有时会换

```python
domain = "generalv3.5"      # Max版本
# domain = "4.0Ultra"  # Ultra版本

Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"   # Max服务地址
# Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat"  # Ultra服务地址
```

##### 4. 输出问题

- 有时候会回答一堆无关紧要的东西，最后都会过滤调应该没事

- 还有会因为出现一些敏感词汇拒绝回答的，本轮就只会返回空列表了

  

#### test.py

1. 命令行参数 — 第 40 行

    选择是否直接从文件中读取提取到次数 > 10 的词汇
    
    - True：从文件读取
    - False: 默认为 False 要计算词频
    
    ```python
    parser.add_argument('--load_original_keys', default=False,
                        type=bool, help='Continue from extracting data')
    ```
    
    在文件 251 行使用 `if not args.load_original_keys:...`
    
2. 文件结构 — 47 行

    ```python
    ├─data
    │     vocab.pkl这些
    │  
    │  
    ├─4_gci_LLM
       │  test.py
       │  yake_pke.py
       │
       ├─datasets
       │
       │
       ├─PythonDemo(content)
       │      SparkApi.py
       │      SparkPythondemo.py
       │
       └─spark_extract
               SparkApi.py
               SparkPythondemo.py
    ```

    主要是上面这样

    ```python
    addr = '../data/' # 修改了需要的文件位置，
    extract_way = '_LLM'	# 要和YAKE做区分，所有保存的文件名都有用到 (或者就改dump_keys和load_dumped_keys应该也可以)
    ```

3. LLM筛选关键词部分 — 215 行

    调用的函数是 `extract_LLM` 

    ```python
    from spark_extract import SparkPythondemo
    def extract_LLM(all_keys):
        ...
        select_keys = SparkPythondemo.get_output(','.join(accu_select), all_keys)
        return select_keys
    ```

4. `dump_keys` 保存关键词到文件 — 279

    文件是存到当前目录的datasets文件夹下的

    ```python
    def dump_keys(df, df_last, threshold=10):
        # threshold 关键词频次
        file_path = 'datasets/original_' + suffix + extract_way + '.txt'
        ...
        print(f'Keys with count > {threshold} have been saved to {file_path}')
    ```

5. `load_dumped_keys` 加载文件 — 295

    ```python
    def load_dumped_keys():
        print("loading dumped keys...")
        ...
        return lines
    ```

6. 其他

    除了打印一些中间量和时间，没有其他会影响结果的改动了
