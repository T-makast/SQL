'''
    Первый скрипт-отчёт
'''
from pathlib import Path
import json
import logging
import jinja2
import matplotlib.pyplot as plt
import pandas as pd

'''
    Настраиваем отправку логов;
'''

logger = logging.getLogger('traceback')
logger.setLevel(logging.INFO)
fh = logging.FileHandler(str(Path(__file__).parents[1]) + '\\traceback.log')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


'''
    Не супер понимаю что здесь происходит но мы настриваем логи;
'''

class ReportConfig:
    def __init__(self):
        self.dsn_path: str = ''
        self.plot_path: str = ''
        self.templates_path: str = ''
        self.report_path: str = ''
        self.is_configured = False

    def configure_from_file(self, path: str) -> None:
        logger.info('Start configuration query 1')
        self.is_configured = False
        with open(path) as f:
            config = json.load(f)
        self.dsn_path = config['dsn_path']
        self.plot_path = config['plot_path']
        self.templates_path = config['templates_path']
        self.report_path = config['report_path']
        self.is_configured = True
        logger.info('Finished configuration query 1')


'''
    Закидываем наш result set в dataframe
'''

def get_data(config: ReportConfig) -> pd.DataFrame:
    query = ''' with set_wood as(
            select
                aux.length_m as "length",
                aux.diameter_cm as "diameter",
                sum(aux.quantity) as "n_items"
            from (
                select
                    g.length_m,
                    g.diameter_cm,
                    oc.quantity,
                    o.ordered_ts
                from orders o
                    join order_contents oc on oc.order_id = o.id
                    join goods g on g.id = oc.good_id
                where extract('year' from o.ordered_ts) = 2018
            ) as aux
            group by "length", "diameter"
            order by "length", "n_items"
        ),
        aux_2 as (
            select
                sw.length,
                sw.diameter,
                sw.n_items,
                row_number() over(partition by sw.length order by sw.n_items desc) as rk
            from set_wood sw
            )
        select
            concat(a.length::int, ' m ', a.diameter, ' cm') as "type",
            a.n_items
        from aux_2 a
        where a.rk = 1
        order by length, diameter '''
    logger.info('Fetching data query 1')
    with open(config.dsn_path) as f:
        dsn = f.read()
    df = pd.read_sql_query(query, dsn)
    logger.info('Fetched data query 1')
    return df


'''
    Задаём размер фигуры и чертим чертежи;
    Сохраняем .png в /resources/plots
'''

def make_plot(df: pd.DataFrame, config: ReportConfig) -> None:
    logger.info('Start plotting query 1')

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(df['type'], df['n_items'], width=0.2, color=(0.1, 0.1, 0.1, 0.1),  edgecolor='blue', align='center')
    ax.set_xlabel('Лучший продаваемый диаметр для каждой длины за 2 года')
    ax.set_ylabel('Количество проданных брёвен в 2018 году, шт.')
    plt.title('Самые продаваемые "диаметры"')

    fig.savefig(config.plot_path, bbox_inches='tight')

    logger.info('Finished plotting query 1')


'''
    Рендерим репорт закидывая всё в темплейт;
'''

def render_report(df, config):
    logger.info('Loading templates query 1')
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(config.templates_path)
    )
    template = env.get_template('sales_report.html')
    logger.info('Rendering report query 1')
    page = template.render(
        title='Задача 5',
        plot_path=config.plot_path,
        table=df.to_html(escape=True),
        description="Для каждой длины бревна найдите, брёвна какого диаметра покупали чаще всего. Выберите все продажи таких брёвен за 2018 год."
    )
    with open(config.report_path, 'w', encoding='UTF8') as f:
        f.write(page)
    logger.info('Rendered report query 1')
    pass


def make_report(config: ReportConfig):
    logger.info('Start making report query 1')
    df = get_data(config)
    make_plot(df, config)
    render_report(df, config)
    logger.info('Report is ready query 1')
    pass


if __name__ == '__main__':
    config = ReportConfig()
    config.configure_from_file(str(Path(__file__).parents[1]) + '\\config\\config_query_1.json')
    make_report(config)

