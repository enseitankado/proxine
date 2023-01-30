
max_secs=$((120*60))
retry_count=1
time_out=4

sort -u proxy/http.txt -o proxy/http.txt

proxy_count=`cat proxy/http.txt | wc -l`
duration=$(( $proxy_count * $retry_count * $time_out))
thread_count=$(( ($duration + $max_secs + 1) / $max_secs))


echo $max_secs
echo $proxy_count
echo $duration
echo $thread_count



php /home/pi/proxy-profiler/proxyprof.php -f proxy/http.txt -t http -a https://www.tankado.com/ -y $retry_count -c $time_out -n $thread_count
