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

url = URI.parse("http://www.#{domain}")
req = Net::HTTP::Get.new('/export?p=1')
res = Net::HTTP.start(url.host, url.port) {|http|
  http.request(req)
}
puts res.class == Net::HTTPOK

f = File.open("backup_files/posts/p1.txt", "w")
f << res.body
f.close

image = res.body.split("\n").first
pp image

req = Net::HTTP::Get.new("/blog-image/#{image}")
res = Net::HTTP.start(url.host, url.port) {|http|
  http.request(req)
}

f = File.open("backup_files/images/#{image}", "w")
f << res.body
f.close
