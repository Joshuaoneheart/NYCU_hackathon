def get_hospital_by_department(department, location):
    import pandas as pd
    from utils.address import get_coordinate
    hospitals = pd.read_csv(open("./open_data/hospital.csv", "r", encoding="utf-8"))
    if department not in hospitals.columns:
        print(hospitals.columns)
        return -1
    hospitals = hospitals[hospitals[department] == "V"]
    return hospitals.head()


def get_nearby_PCR(location):
    import pandas as pd
    pcrs = pd.read_csv(open("./open_data/covid-19.csv", "r", encoding="utf-8"))
    kf = lambda row: (float(row.values[-2]) - location[0])**2 + (float(row.values[-1]) - location[1])**2
    # print(pcrs.apply(kf, axis=1)[pcrs.apply(kf, axis=1).argsort()])
    return pcrs["機構名稱"][pcrs.apply(kf, axis=1).argsort(axis=1)].head(1).values[0]
    
