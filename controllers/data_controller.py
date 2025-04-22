from db.db import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam
from datetime import datetime, timedelta
from models.data_models import ChartData, ChartDataSet, TableData


def get_multidate_market_value(ids, begin, end, num_points, entity_type):
    dates = [date.strftime("%m-%d-%Y") for date in get_dates(begin, end, num_points)]

    ids_names = get_names(ids, entity_type)

    chart_data_set = ChartDataSet(
        dates=dates,
        chart_data_list=[],
    )

    for id, name in ids_names:
        chart_data = ChartData(name=name, values=[])

        for date in dates:
            if entity_type == "Pos":
                chart_data.values.append(
                    round(float(get_position_market_value(id, date)), 2)
                )
            else:
                chart_data.values.append(
                    round(float(get_account_market_value(id, date)), 2)
                )

        chart_data_set.chart_data_list.append(chart_data)

    return chart_data_set


def get_multidate_twr(ids, begin, end, num_points, entity_type):
    dates = [date.strftime("%m-%d-%Y") for date in get_dates(begin, end, num_points)]

    ids_names = get_names(ids, entity_type)

    chart_data_set = ChartDataSet(
        dates=dates,
        chart_data_list=[],
    )

    for id, name in ids_names:
        chart_data = ChartData(name=name, values=[])

        for date in dates:
            if entity_type == "Pos":
                chart_data.values.append(
                    round(float(get_position_twr(id, dates[0], date)) * 100, 2)
                )
            else:
                chart_data.values.append(
                    round(float(get_account_twr(id, dates[0], date)) * 100, 2)
                )

        chart_data_set.chart_data_list.append(chart_data)

    return chart_data_set


def get_asset_allocation(ids, date, entity_type):
    types_values = None

    chart_data_set = ChartDataSet(
        dates=[date],
        chart_data_list=[],
    )

    if entity_type == "Pos":
        types_values = get_position_asset_allocation(ids, date)
    else:
        types_values = get_account_asset_allocation(ids, date)

    for type, value in types_values:
        chart_data_set.chart_data_list.append(
            ChartData(
                name=type,
                values=[value],
            )
        )

    return chart_data_set


def get_table_values(ids, begin, end, entity_type):
    raw_table_values = None

    headers = []

    names = get_names(ids, entity_type)

    if entity_type == "Pos":
        raw_table_values = get_position_table_values(ids, begin, end)
        headers = ["Investment", "Begin Balance", "End Balance", "Return %"]
    else:
        raw_table_values = get_account_table_values(ids, begin, end)
        headers = ["Account", "Begin Balance", "End Balance", "Return %"]

    table_values = []

    for name, row in zip(names, raw_table_values):
        table_values.append(
            (
                name,
                f"${round(float(row[1]), 2)}",
                f"${round(float(row[2]), 2)}",
                f"{round(float(row[3]) * 100, 2)}%",
            )
        )

    table = TableData(
        cols=4,
        headers=headers,
        separate_bottom=False,
        data=[item for tuple in table_values for item in tuple],
    )

    return table


def get_all_entities():
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                    SELECT p.PositionID, i.Ticker, p.AccountID FROM Investment i
                    INNER JOIN Position p ON p.InvestmentID = i.InvestmentID
                    """
            )
        )

        raw_positions = result.fetchall()

        if not raw_positions:
            return None

        result = session.execute(
            text(
                """
                    SELECT AccountID, Registration, AccountNumber FROM Account
                    """
            )
        )

        raw_accounts = result.fetchall()

        if not raw_accounts:
            return None

        entities_list = []

        for row in raw_positions:
            entities_list.append((f"Pos{row[0]}", f"{row[1]}", f"Acc{row[2]}"))

        for row in raw_accounts:
            entities_list.append((f"Acc{row[0]}", f"{row[1]} x{row[2][-4:]}", None))

        entities = {}

        for entity in entities_list:
            data = {"name": entity[1], "types": []}

            if entity[2]:
                data["parent"] = entity[2]

            entities[entity[0]] = data

        return entities


def get_dates(begin, end, num_dates):
    begin_date = datetime.strptime(begin, "%m/%d/%Y")
    end_date = datetime.strptime(end, "%m/%d/%Y")

    if num_dates < 2:
        return [begin_date]

    delta = (end_date - begin_date) / (num_dates - 1)

    return [begin_date + i * delta for i in range(num_dates)]


def get_names(ids, entity_type):
    if entity_type == "Pos":
        with SessionLocal() as session:
            result = session.execute(
                text(
                    """
                    SELECT p.PositionID, i.Ticker FROM Investment i
                    INNER JOIN Position p ON p.InvestmentID = i.InvestmentID
                    WHERE p.PositionID IN :position_ids
                    """
                ).bindparams(bindparam("position_ids", expanding=True)),
                {
                    "position_ids": ids,
                },
            )

            rows = result.fetchall()

            if not rows:
                return None

            names = []

            for row in rows:
                names.append(f"{row[1]}")

            return names
    else:
        with SessionLocal() as session:
            result = session.execute(
                text(
                    """
                    SELECT AccountID, Registration, AccountNumber FROM Account
                    WHERE AccountID IN :account_ids
                    """
                ).bindparams(bindparam("account_ids", expanding=True)),
                {
                    "account_ids": ids,
                },
            )

            rows = result.fetchall()

            if not rows:
                return None

            names = []

            for row in rows:
                names.append(f"{row[1]} x{row[2][-4:]}")

            return names


def get_position_market_value(position_id, date):
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                SELECT EndVal FROM DailyPerformance 
                WHERE PositionID = :position_id AND ValDate = :date
                """
            ),
            {
                "position_id": position_id,
                "date": date,
            },
        )

        row = result.fetchone()

        return row[0] if row else None


def get_account_market_value(account_id, date):
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                SELECT SUM(EndVal) FROM DailyPerformance
                INNER JOIN Position ON Position.PositionID = DailyPerformance.PositionID
                WHERE Position.AccountID = :account_id AND DailyPerformance.ValDate = :date
                GROUP BY Position.AccountID
                """
            ),
            {
                "account_id": account_id,
                "date": date,
            },
        )

        row = result.fetchone()

        return row[0] if row else None


def get_position_twr(position_id, begin, end):
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                SELECT dbo.GetPositionTWR(:position_id, :begin, :end)
                """
            ),
            {
                "position_id": position_id,
                "begin": begin,
                "end": end,
            },
        )

        row = result.fetchone()

        return row[0] if row else None


def get_account_twr(account_id, begin, end):
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                SELECT dbo.GetAccountTWR(:account_id, :begin, :end)
                """
            ),
            {
                "account_id": account_id,
                "begin": begin,
                "end": end,
            },
        )

        row = result.fetchone()

        return row[0] if row else None


def get_position_asset_allocation(position_ids, date):
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                SELECT i.Type, SUM(dp.EndVal) AS Total FROM DailyPerformance dp
                INNER JOIN Position p ON p.PositionID = dp.PositionID
                INNER JOIN Investment i ON i.InvestmentID = p.InvestmentID
                WHERE dp.ValDate = :date AND p.PositionID in :position_ids
                GROUP BY i.Type
                """
            ).bindparams(bindparam("position_ids", expanding=True)),
            {
                "position_ids": position_ids,
                "date": date,
            },
        )

        rows = result.fetchall()

        return rows if rows else None


def get_account_asset_allocation(account_ids, date):
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                SELECT i.Type, SUM(dp.EndVal) AS Total FROM DailyPerformance dp
                INNER JOIN Position p ON p.PositionID = dp.PositionID
                INNER JOIN Investment i ON i.InvestmentID = p.InvestmentID
                WHERE dp.ValDate = :date AND p.AccountID in :account_ids
                GROUP BY i.Type
                """
            ).bindparams(bindparam("account_ids", expanding=True)),
            {
                "account_ids": account_ids,
                "date": date,
            },
        )

        rows = result.fetchall()

        return rows if rows else None


def get_position_table_values(position_ids, begin, end):
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                SELECT i.Ticker, 
                (SELECT EndVal FROM DailyPerformance WHERE ValDate = :begin AND PositionID = p.PositionID) AS BeginValue,
                (SELECT EndVal FROM DailyPerformance WHERE ValDate = :end AND PositionID = p.PositionID) AS EndValue,
                dbo.GetPositionTWR(p.PositionID, :begin, :end) AS TWR
                FROM Position p
                INNER JOIN Investment i ON i.InvestmentID = p.PositionID
                WHERE p.PositionID in :position_ids
                """
            ).bindparams(bindparam("position_ids", expanding=True)),
            {
                "position_ids": position_ids,
                "begin": begin,
                "end": end,
            },
        )

        rows = result.fetchall()

        return rows if rows else None


def get_account_table_values(account_ids, begin, end):
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                SELECT a.Registration, 
                (SELECT SUM(EndVal) FROM DailyPerformance
                INNER JOIN Position ON Position.PositionID = DailyPerformance.PositionID
                WHERE Position.AccountID = a.AccountID AND DailyPerformance.ValDate = :begin
                GROUP BY Position.AccountID) AS BeginValue,
                (SELECT SUM(EndVal) FROM DailyPerformance
                INNER JOIN Position ON Position.PositionID = DailyPerformance.PositionID
                WHERE Position.AccountID = a.AccountID AND DailyPerformance.ValDate = :end
                GROUP BY Position.AccountID) AS EndValue,
                dbo.GetAccountTWR(a.AccountID, :begin, :end) AS TWR
                FROM Account a
                WHERE a.AccountID in :account_ids
                """
            ).bindparams(bindparam("account_ids", expanding=True)),
            {
                "account_ids": account_ids,
                "begin": begin,
                "end": end,
            },
        )

        rows = result.fetchall()

        return rows if rows else None


# def get_household_market_value(household_id, date):
# with SessionLocal() as session:
# result = session.execute(
# text(
# """
# SELECT SUM(EndVal) FROM DailyPerformance
# INNER JOIN Position ON Position.PositionID = DailyPerformance.PositionID
# INNER JOIN Account ON Account.AccountID = Position.AccountID
# WHERE Account.HouseholdID = :household_id AND DailyPerformance.ValDate = :date
# GROUP BY Account.HouseholdID
# """
# ),
# {
# "household_id": household_id,
# "date": date,
# },
# )
#
# row = result.fetchone()
#
# return row[0] if row else None
#
# def get_household_twr(household_id, begin, end):
# with SessionLocal() as session:
# result = session.execute(
# text(
# """
# SELECT dbo.GetHouseholdTWR(:household_id, :begin, :end)
# """
# ),
# {
# "household_id": household_id,
# "begin": begin,
# "end": end,
# },
# )
#
# row = result.fetchone()
#
# return row[0] if row else None
