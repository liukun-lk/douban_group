# frozen_string_literal: true

class DoubanSpider < ApplicationSpider
  USER_AGENTS = %w[Chrome Firefox Safari Opera].freeze

  @name = 'douban_spider'
  base_urls = ['https://www.douban.com/group/145219/discussion']
  @start_urls = base_urls.map { |base_url| (0..7).map { |i| URI("#{base_url}?start=#{i * 25}").to_s } }.flatten
  @config = {
    user_agent: -> { USER_AGENTS.sample }
  }

  def parse(response, url:, data: {})
    # 去掉 table 的头部内容
    response.xpath("//table[@class='olt']/tr")[1..-1].each do |element|
      children = element.element_children
      url      = children[0].children.at_xpath('@href').value

      item = {
        title: children[0].text.strip,
        url: url,
        author: children[1].text,
        reply: children[2].text.to_i,
        last_reply_time: children[3].text.to_time,
        topic_id: url.match(/\d+/).to_s,
        created_at: Time.now
      }

      send_item item, saver: { table: :topic_lists }

      request_to :parse_topic_detail_page, url: url
    end
  end

  def parse_topic_detail_page(response, url:, data: {})
    title        = (response.at_xpath("//td[@class='tablecc']") || response.at_xpath("//div[@id='content']/h1"))&.text&.strip
    return unless title
    published_at = response.at_xpath("//span[@class='color-green']").text.to_time
    author       = response.at_xpath("//span[@class='from']/a").text
    content      = (response.at_xpath("//div[@class='topic-content']/p") || response.at_xpath("//div[@class='topic-content']")).text.strip
    images       = response.xpath("//*[@id='link-report']//img/@src").map(&:value).join(',')
    topic_id     = url.match(/\d+/).to_s

    item = {
      title: title,
      created_at: Time.now,
      published_at: published_at,
      author: author,
      content: content,
      images: images,
      topic_id: topic_id,
      url: url
    }

    send_item item, saver: { table: :topics }
  end
end
