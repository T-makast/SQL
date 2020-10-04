'''
    Третий (читайте script_1.py)
'''
from pathlib import Path
import json
import logging
import jinja2
import matplotlib.pyplot as plt
import pandas as pd


logger = logging.getLogger('traceback')
logger.setLevel(logging.INFO)
fh = logging.FileHandler(str(Path(__file__).parents[1]) + '\\traceback.log')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


class ReportConfig:
    def __init__(self):
        self.dsn_path: str = ''
        self.plot_path: str = ''
        self.templates_path: str = ''
        self.report_path: str = ''
        self.is_configured = False

    def configure_from_file(self, path: str) -> None:
        logger.info('Start configuration query 3')
        self.is_configured = False
        with open(path) as f:
            config = json.load(f)
        self.dsn_path = config['dsn_path']
        self.plot_path = config['plot_path']
        self.templates_path = config['templates_path']
        self.report_path = config['report_path']
        self.is_configured = True
        logger.info('Finished configuration query 3')


def get_data(config: ReportConfig) -> pd.DataFrame:
    query = '''select 
            aux.month,
	        aux.client_type,
            sum(rev) as "revenue"
        from(
            select 
                coalesce(c.client_type, 'розница') as "client_type",
                to_char(date_trunc('month', o.ordered_ts), 'YYYY-MM') as "month",
                    g.length_m, (oc.quantity * p.price) as "rev"
            from orders o 
            join order_contents oc
                on o.id=oc.order_id
                left join clients c on c.id=o.client_id
                join goods g on oc.good_id=g.id
                join wood_types wt on wt.id=g.wood_type_id
                join prices p on p.good_id = g.id and extract('year' from o.ordered_ts)=extract('year' from p.date_start)
            where for_ships or for_houses
            ) as aux
        where length_m > 10
        group by aux.month, aux.client_type
        order by aux.month, revenue desc'''
    logger.info('Fetching data query 3')
    with open(config.dsn_path) as f:
        dsn = f.read()
    df = pd.read_sql_query(query, dsn)
    logger.info('Fetched data query 3')
    return df


def make_plot(df: pd.DataFrame, config: ReportConfig) -> None:
    logger.info('Start plotting query 3')
    fig = plt.figure(figsize=(12, 4))
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(df.iloc[::3, 0], df.iloc[::3, 2], label='розница')
    ax.plot(df.iloc[::3, 0], df.iloc[1::3, 2], label='верфи')
    ax.plot(df.iloc[::3, 0], df.iloc[2::3, 2], label='торговцы')
    ax.set_xlabel('Месяцы')
    ax.set_ylabel('Выручка, рублей')
    plt.title('Выручка в разрезе летних месяцев разными типами клиентов')
    plt.legend(["Розница", "Верфи", "Торговцы"])
    fig.savefig(config.plot_path, bbox_inches='tight')
    logger.info('Finished plotting query 3')


def render_report(df, config):
    logger.info('Loading templates query 3')
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(config.templates_path)
    )
    template = env.get_template('sales_report.html')
    logger.info('Rendering report query 3')
    page = template.render(
        title='Задача 1',
        plot_path=config.plot_path,
        table=df.to_html(escape=True),
        description="Рассчитайте выручку от покупок брёвен длиной более 10 метров, которые можно использовать для строительства домов или кораблей. Расчёт нужен в разрезе месяцев и типов клиента (верфи, торговцы, розница)."
    )
    with open(config.report_path, 'w', encoding='UTF8') as f:
        f.write(page)
    logger.info('Rendered report query 3')
    pass


def make_report(config: ReportConfig):
    logger.info('Start making report query 3')
    df = get_data(config)
    make_plot(df, config)
    render_report(df, config)
    logger.info('Report is ready query 3')
    pass


if __name__ == '__main__':
    config = ReportConfig()
    config.configure_from_file(str(Path(__file__).parents[1]) + '\\config\\config_query_3.json')
    make_report(config)

