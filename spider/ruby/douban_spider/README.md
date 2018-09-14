# 豆瓣爬虫 Kimurai 版

这是使用 [Kimurai](https://github.com/vifreefly/kimuraframework)（一个由 Ruby 编写的爬虫框架）爬取豆瓣租房小组的例子。

## 安装

直接运行 `bundle install` 安装 Gemfile 里面的 gem 包。

## 运行

1. 创建数据库并创建表：`rake db:create db:migrate`
2. 删除数据库：`rake db:drop`
3. 回滚数据库：`rake db:migrate[0]`(0 表示回滚所有表)
4. 执行爬虫：`bundle exec kimurai runner -j 3`

## 调试

```
# https://github.com/vifreefly/kimuraframework#interactive-console

kimurai console --engine selenium_chrome --url https://github.com/vifreefly/kimuraframework
```
