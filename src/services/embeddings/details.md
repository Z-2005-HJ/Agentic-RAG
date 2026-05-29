## Jina_client

- 创建一个JinaEmbeddingsClient，把链接远程API所需的所有信息准备好，包含jina API key、jina URL、header等。
- 把一批传入的文本批量拆开，然后异步发送HTTP请求到jina里面进行embedding，然后把向量化之后的结果都加入总列表。
- 把用户传入的问题也按照相同的方式向量化，然后放到query列表里面
- 最后aclose释放连接资源
- 最后的_aenter_和_aexit_是配合异步用法的协议方法

## factory

- 从配置里读取API key和URL，然后调用JinaEmbeddingsClient真正形成可以干活的向量客户端
