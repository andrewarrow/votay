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

ran = rand(9999999999)
File.makedirs("backup_files#{ran}/posts")
File.makedirs("backup_files#{ran}/images")

domain = 'votay.com'  # change to your domain
page = 1

while true
  url = URI.parse("http://www.#{domain}")
  req = Net::HTTP::Get.new("/export?p=#{page}")
  res = Net::HTTP.start(url.host, url.port) do |http|
    http.request(req)
  end

  break if res.class != Net::HTTPOK

  lines = res.body.split("\n")
  permalink = lines[2].gsub(/\//,'_')
  
  f = File.open("backup_files#{ran}/posts/#{permalink}.txt", "w")
  f << res.body
  f.close
  
  image = lines[0]
  pp image
  
  req = Net::HTTP::Get.new("/blog-image/#{image}")
  res = Net::HTTP.start(url.host, url.port) do |http|
    http.request(req)
  end
  
  f = File.open("backup_files#{ran}/images/#{image}", "w")
  f << res.body
  f.close
  
  puts 'sleeping'
  sleep(5)
  page += 1
end