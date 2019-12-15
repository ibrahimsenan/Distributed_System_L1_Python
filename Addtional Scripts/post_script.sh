
for i in {1..4};
do
	curl -d 'entry=entry1^'${i} -X 'POST' 'http://10.1.0.1:80/board' &
	curl -d 'entry=entry5^'${i} -X 'POST' 'http://10.1.0.5:80/board' &
	curl -d 'entry=entry8^'${i} -X 'POST' 'http://10.1.0.8:80/board' &
	curl -d 'entry=entry3^'${i} -X 'POST' 'http://10.1.0.3:80/board'
done
