#!/usr/local/bin/ruby
#Ruby script to hit a votay blog at
#http://domain.com/export?p=1
#http://domain.com/export?p=2
#http://domain.com/export?p=3
#etc until you get a 404 response

require 'rubygems'
require 'net/http'
require 'uri'
require 'pp'
require 'ftools'

File.makedirs('backup_files/posts')
File.makedirs('backup_files/images')

domain = 'votay.com'  # change to your domain
page = 1

while true
  url = URI.parse("http://www.#{domain}")
  req = Net::HTTP::Get.new("/export?p=#{page}")
  res = Net::HTTP.start(url.host, url.port) do |http|
    http.request(req)
  end

  break if res.class != Net::HTTPOK
  
  f = File.open("backup_files/posts/p#{page}.txt", "w")
  f << res.body
  f.close
  
  image = res.body.split("\n").first
  pp image
  
  req = Net::HTTP::Get.new("/blog-image/#{image}")
  res = Net::HTTP.start(url.host, url.port) do |http|
    http.request(req)
  end
  
  f = File.open("backup_files/images/#{image}", "w")
  f << res.body
  f.close
  
  puts 'sleeping'
  sleep(5)
  page += 1
end