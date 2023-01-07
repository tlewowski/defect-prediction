import argparse
import csv
import os


class MetricsData:

    def __init__(self, header, data, join_on_names):
        self.header = header
        self.join_on_names = join_on_names
        self.join_on_indices = [header.index(j) for j in join_on_names]
        self.contributed_indices = [i for i in range(0, len(header)) if i not in self.join_on_indices]
        self.data = [(self.key(record), self.entry(record)) for record in data]
        if len(join_on_names) > 0:
            self.data.sort(key=lambda x: "_".join(x[0]))

    def empty_record(self):
        return [[None] * len(self.join_on_indices), [None] * len(self.contributed_indices)]

    def key(self, record):
        return [record[v] for v in self.join_on_indices]

    def entry(self, record):
        print(len(record), record)
        return [record[v] for v in self.contributed_indices]
    @staticmethod
    def join_all(metrics_data_sets):
        indices = [[0, ds] for ds in metrics_data_sets]
        complete_header = MetricsData.join_headers(metrics_data_sets)

        data_records = []
        while True:
            candidate_rows = []
            any_candidate = False
            for i in indices:
                if i[0] < len(i[1].data):
                    candidate_rows.append((i[1], i[1].data[i[0]]))
                    any_candidate = True
                else:
                    candidate_rows.append([i[1], i[1].empty_record()])

            if not any_candidate:
                break

            smallest = []
            for k in range(len(candidate_rows)):
                if candidate_rows[k][1] is not None:
                    if len(smallest) == 0:
                        smallest.append(k)
                    else:
                        if smallest[0] == candidate_rows[k][1]:
                            smallest.append(k)
                        elif smallest[0] > candidate_rows[k][1]:
                            smallest.clear()
                            smallest.append(k)

            row = []
            for k in range(len(candidate_rows)):
                if k in smallest:
                    row.append(candidate_rows[k][1][1])
                else:
                    row.append(candidate_rows[k][0].empty())

            data_records.append(row)

            for s in smallest:
                indices[s][0] = indices[s][0] + 1

        return MetricsData(complete_header, data_records, [])

    @staticmethod
    def join_headers(metrics_data_sets):
        descriptors = [metrics_data_sets[0].header[i] for i in metrics_data_sets[0].join_on_indices]
        descriptors.append([m.header[i] for m in metrics_data_sets for i in m.contributed_indices])
        return descriptors

def parser():
    p = argparse.ArgumentParser(description="Merge metrics from tools into single CSV file")
    p.add_argument("--input", type=str, nargs="+", help="files with metrics to merge", required=True)
    p.add_argument("--join_on", type=str, nargs="+", help="name of column on which to match", required=True)
    p.add_argument("--target_file", type=str, help="location of final file with metrics", required=True)
    return p


def run_as_main():
    args = parser().parse_args()
    with open(args.target_file, mode="w", encoding="utf-8") as f:
        metrics_data = []
        for i in args.input:
            if not os.path.isfile(i):
                raise RuntimeError("{} is not a file".format(i))
            with open(i, mode="r", encoding="utf-8") as m:
                reader = csv.reader(m, delimiter=',')
                header = next(reader)
                metrics_data.append(MetricsData(header, [r for r in reader], args.join_on))

        final_dataset = MetricsData.join_all(metrics_data)
        writer = csv.writer(f)
        writer.writerow(final_dataset.header)
        writer.writerows(final_dataset.data)


if __name__ == "__main__":
    run_as_main()