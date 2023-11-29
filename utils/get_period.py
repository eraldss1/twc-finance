def get_period_time(file_name):
    period_time = file_name.split(".")[0].replace("TWCFIN", "").title()
    period_time = period_time[:3] + "_" + period_time[3:-4]
    return period_time
