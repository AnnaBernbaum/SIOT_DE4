from os import listdir

# Get files to read from
path_to_dir = "LightDogs/data"
filenames = listdir(path_to_dir)
csvs = [filename for filename in filenames if filename.endswith(".csv")]

# Open files to write to
l_out=open("l_out.csv", "a")
t_out=open("t_out.csv", "a")

# Write to CSVs
for csv in csvs:
    # Insert Light Data
    print(csv)
    if "LightLevels" in csv:
        for line in open(path_to_dir + '/' + csv):
            # csv.next()
            l_out.write(line)

    # Insert Twitter Data
    elif "Tweets" in csv:
        for line in open(path_to_dir + '/' + csv):
            # csv.next()
            t_out.write(line)