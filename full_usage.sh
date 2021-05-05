rm -r  mid/queries/nott_mini_chords 2>/dev/null
deactivate 2>/dev/null
source venv/bin/activate # replace with your virtual environment if its different

echo "create an index from a subset of the nottingham dataset, using the graph based algorithm with chords"
echo ">python segment.py --algorithm graph --melody_track 0 --chord_track 1 mid/nottingham-mini/*.mid -o nott_mini_chords"
sleep .5
python segment.py --algorithm graph --melody_track 0 --chord_track 1 mid/nottingham-mini/*.mid -o nott-mini_chords
echo "Created index. Using create_query_midis.py: create some sample indexed queries"
echo ">python create_query_midis.py --rng_seed 0 mid/nottingham-mini/ 20 nott_mini_queries indexed --algorithm graph --melody_track 0 --chord_track 1"
sleep 2
python create_query_midis.py --rng_seed 0 mid/nottingham-mini/ 20 nott_mini_queries indexed --algorithm graph --melody_track 0 --chord_track 1

echo "creating queries done: now test one of these queries on the query by example algorithm for graphs"

for mid in mid/queries/nott_mini_queries/*.mid; do
  sleep 3
  echo ">python query_file.py --algorithm graph --melody_track 0 --chord_track 1 --use_minimum $mid nott_mini_chords"
  python query_file.py --algorithm graph --melody_track 0 --chord_track 1 --use_minimum "$mid" nott_mini_chords
done


deactivate