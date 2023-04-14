import os
import dash_bootstrap_components as dbc
import hashlib
import pandas as pd

from dash import callback,dcc, html, Input, Output, State, ctx, dash_table, get_asset_url, exceptions
from PIL import ImageGrab
from .config import features, DBNAME, tooltip_delay



def generate_table(df, reverse=False):
    df = df.iloc[::-1 if reverse else 1]
    return dash_table.DataTable(
        id='datatable',
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": True} 
            for i in df.columns if i not in ['id','filenames']
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable=False,
        row_selectable=False,
        row_deletable=False,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 5,
    )

def get_stat(df):
    ps = []
    cols = [f for f,k in features if f not in ['PNL','Datetime']]
    overall = df.loc[:,cols].sum(axis=0).to_frame()
    swap = df[df['Контр тренд']==1].loc[:,cols].sum(axis=0).to_frame()
    pnlp = df[df['PNL']=='+'].loc[:,cols].sum(axis=0).to_frame()
    pnlm = df[df['PNL']=='-'].loc[:,cols].sum(axis=0).to_frame()
    pnl = pd.concat([pnlp,pnlm],axis=1,ignore_index=True).apply(lambda r: f'{r[0]}/{r[1]}',axis=1).to_frame()
    # overall.reset_index(drop=False, inplace=True)
    # swap.reset_index(drop=False, inplace=True)

    report = pd.concat([overall,swap,pnl],axis=1)
    report = report.reset_index(drop=False)
    report.columns = ['index','Всего','Конт тренд','PNL +/-']
    return dbc.Table.from_dataframe(report, hover=True)

def get_db(db_name):
    if not os.path.exists(db_name):
        df = pd.DataFrame(columns=['ticker']+[f for f,v in features]+['filenames'])
    else:
        df = pd.read_csv(
            db_name,
            header=0,
            index_col=None,
        )
    df['id']=df.index
    return df

df = get_db(DBNAME)



layout = html.Div([
    html.Div([
            html.H2('Info about count rows:', className='label label-info ms-0', id='info_header'),
            html.Div([
                dbc.Button(
                    html.I(
                        className='bi bi-sort-alpha-down', 
                        id='reverse_icon'
                    ),
                    id='reverse_btn',
                    color='info',
                    outline=True,
                    n_clicks=0,
                    className='me-1 col-sm-auto d-flex align-items-center'),
                dbc.Button(
                    html.I(className='bi bi-arrow-clockwise'),
                    id='reload_db',
                    color='info',
                    outline=True,
                    className='me-1 col-sm-auto d-flex align-items-center'),
                dbc.Button(
                    html.I(className='bi bi-fullscreen'),
                    id='open_fullscreen',
                    color='info',
                    outline=True,
                    className='me-1 col-sm-auto d-flex align-items-center'),
                dbc.Tooltip(
                    'Reload DataBase',
                    target='reload_db',
                    placement='left',
                    delay=tooltip_delay),
                dbc.Tooltip(
                    'Preview Trades',
                    target='open_fullscreen',
                    placement='left',
                    delay=tooltip_delay),
                dbc.Tooltip(
                    'Reverse Table',
                    target='reverse_btn',
                    placement='left',
                    delay=tooltip_delay),
            ], className='row'),
        ],
        className='d-flex justify-content-between pb-2'
    ),
    html.Div(generate_table(df), id='table-container'),
    html.Div(get_stat(df), className='label label-info', id='table-stat'),
    html.Div([
        dbc.NavLink(
            dbc.Button(
                html.I(className='bi bi-journal-plus fs-2'),
                outline=False,
                className='btn btn-info',
                id='new_trade_btn',
            ),
            href="/new_trade",
        ),
        dbc.Tooltip(
            'Add new trade',
            target='new_trade_btn',
            placement='left',
            delay=tooltip_delay),
        ],
        className='d-flex flex-column align-items-end fixed-bottom me-3 mb-3'
    ),

    dbc.Modal([
            dbc.ModalBody([
                html.Div(className='cursor', children=[
                    dbc.Carousel(
                        items = [ ],
                        controls=True,
                        indicators=False,
                        interval=None,
                        id='img_modal_carousel',
                    ),
                    html.Div(className='vt'),
                    html.Div(className='hl'),
                ]),
                html.P(className='text-black-50', id='filename')
            ]),
        ],
        id="modal-fs",
        fullscreen=True,
    ),
    ],
    className='p-3'
)

@callback(
    Output('info_header', 'children'),
    Output('img_modal_carousel','items'),
    Output('img_modal_carousel','active_index'),
    Output('table-stat','children'),
    Input('datatable', 'derived_virtual_row_ids'),
)
def filtering_df(ids):
    if ids is None:
        raise exceptions.PreventUpdate
    data = df.loc[ids]
    imgs = [
        {'key':2*i+k, 'src':f'{get_asset_url(os.path.join("snapshots",f))}'} 
        for i,fs in enumerate(df.loc[ids].loc[:,'filenames'].values)
        for k,f in enumerate(fs.replace("'",'').strip('][').split(', '))
    ]
    return f'Count: {len(ids)}    PNL count:{len(data[data["PNL"]=="+"])}/{len(data[data["PNL"]=="-"])}', imgs, 0, get_stat(data)

@callback(
    Output('modal-fs','is_open'),
    Input('open_fullscreen','n_clicks'),
    State("modal-fs", "is_open"),
)
def fullscreen(n,is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output('filename','children'),
    Input('img_modal_carousel','active_index'),
    State('img_modal_carousel','items')
)
def filename_callback(index,items):
    return items if len(items)==0 else items[index]['src'].split('/')[-1]

@callback(
        Output('table-container','children'),
        Output('reverse_icon', 'className'),
        Input('reload_db','n_clicks'),
        Input('reverse_btn','n_clicks')
)
def update_table(n,r_clicks):
    trg = ctx.triggered_id
    if trg == 'reload_db':
        global df
        df = get_db(DBNAME)
    return (generate_table(df,r_clicks%2==0),
           'bi bi-sort-alpha-down-alt' if r_clicks%2==0 else 'bi bi-sort-alpha-down')
