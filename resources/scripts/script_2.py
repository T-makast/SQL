'''
    Второй (читайте script_1.py)
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
        logger.info('Start configuration query 2')
        self.is_configured = False
        with open(path) as f:
            config = json.load(f)
        self.dsn_path = config['dsn_path']
        self.plot_path = config['plot_path']
        self.templates_path = config['templates_path']
        self.report_path = config['report_path']
        self.is_configured = True
        logger.info('Finished configuration query 2')


def get_data(config: ReportConfig) -> pd.DataFrame:
    query = '''select 
            weeks."date"::date as "week",
            coalesce(sum(oc.quantity), 0) as "n_items",
            coalesce(sum(oc.quantity), 0) - lag(coalesce(sum(oc.quantity), 0)) over (order by weeks."date"::date) as delta
        from orders o
            join order_contents oc on o.id = oc.order_id
            join goods g on g.id = oc.good_id
            join wood_types wt on wt.id = g.wood_type_id
            right join (
                select 
                    generate_series(
                    date_trunc('week', '2017-06-01'::date),
                    '2017-08-31'::date,
                    '1 week'::interval)
            ) as weeks("date") on weeks."date" = date_trunc('week', o.ordered_ts)
        group by weeks."date"
        order by weeks."date"'''
    logger.info('Fetching data query 2')
    with open(config.dsn_path) as f:
        dsn = f.read()
    df = pd.read_sql_query(query, dsn)
    logger.info('Fetched data query 2')
    return df


def make_plot(df: pd.DataFrame, config: ReportConfig) -> None:
    logger.info('Start plotting query 2')
    fig = plt.figure(figsize=(12, 4))
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(df['week'], df['n_items'], label='Продажи в брёвнах')
    ax.bar(df['week'], df['delta'], width=2, color=(0.1, 0.1, 0.1, 0.1),  edgecolor='blue', align='center')
    ax.set_xlabel('Время')
    ax.bar(df.iloc[6, 0], 1, width=86, color=(0.1, 0.1, 0.1, 0.1), edgecolor='blue', align='center', label='Вместо оси Х')
    ax.set_ylabel('Количество брёвен, шт.')
    plt.title('Продажи брёвен в штуках летом 2017 года')
    plt.legend(["Динамика продаж", "Разница в продажах с предыдущей неделей"])
    fig.savefig(config.plot_path, bbox_inches='tight')
    logger.info('Finished plotting query 2')


def render_report(df, config):
    logger.info('Loading templates query 2')
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(config.templates_path)
    )
    template = env.get_template('sales_report.html')
    logger.info('Rendering report query 2')
    page = template.render(
        title='Задача 4',
        plot_path=config.plot_path,
        table=df.to_html(escape=True),
        description="Найдите динамику количества покупок в разрезе недель за лето 2017 года и найдите изменения относительно предыдущей недели."
    )
    with open(config.report_path, 'w', encoding='UTF8') as f:
        f.write(page)
    logger.info('Rendered report query 2')
    pass


def make_report(config: ReportConfig):
    logger.info('Start making report query 2')
    df = get_data(config)
    make_plot(df, config)
    render_report(df, config)
    logger.info('Report is ready query 2')
    pass


if __name__ == '__main__':
    config = ReportConfig()
    config.configure_from_file(str(Path(__file__).parents[1]) + '\\config\\config_query_2.json')
    make_report(config)

