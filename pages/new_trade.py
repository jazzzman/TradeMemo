import os
import dash_bootstrap_components as dbc
import hashlib
import pandas as pd

from datetime import datetime
from dash import callback, dcc, html, Input, Output, State, ctx, get_asset_url
from PIL import ImageGrab, Image
from .config import features, DBNAME, tooltip_delay


IMG15=None
IMG3=None
file_names={'img15':'','img3':''}

def get_img_clipboard():
    img = ImageGrab.grabclipboard()
    if type(img) is list:
        img = Image.open(img[0])
    return img



layout = dbc.Container([
    dbc.Row([
        dbc.Form([
                dbc.InputGroup([
                    dbc.InputGroupText("Ticker"), 
                    dbc.Input(placeholder="...",type='text',id='ticker'),
                    dbc.FormFeedback("Set the Ticker", type="invalid"),
                ], className='pb-1'),
                dbc.InputGroup([
                    dbc.InputGroupText("Дата"), 
                    dbc.Input(value = f"{datetime.now().strftime('%d.%m.%Y')}",type='text',id='datefield'),
                    dbc.FormFeedback("Неверный формат даты. Пример: 02.12.2023", type="invalid"),
                ], className='py-1'),
                dbc.Checklist(
                    options=[{'label':f,'value':i} for i,(f,v) in enumerate(features) if f not in ['PNL','Datetime']],
                    value=[],
                    id='checklist',
                    className='py-1'),
                dbc.InputGroup([
                    dbc.InputGroupText("PNL:"),
                    dbc.Select(
                        options=[
                            {"label": "Not applicable", "value": 'NA'},
                            {"label": "Positive", "value": '+'},
                            {"label": "Negative", "value": '-'},
                            {"label": "Zero", "value": '0'},
                        ],
                        value=0,
                        id='pnl_select',
                    ),
                ]),
                dbc.Alert(
                    'There is no image in clipboard',
                    id="img-alert",
                    is_open=False,
                    color='warning',
                    duration=4000,
                    className='mt-2',
                ),
                dbc.Alert(
                    'DB updated',
                    id="updated-alert",
                    is_open=False,
                    color='success',
                    duration=4000,
                    className='mt-2',
                ),
                html.Div([
                    dbc.Button(
                        html.Span([
                            html.I(className='bi bi-save2', style=dict(paddingRight='.5vw')),
                            'Фон']),
                        id='save_15min',
                        className="me-1"),
                    dbc.Button(
                        html.Span([
                            html.I(className='bi bi-save2', style=dict(paddingRight='.5vw')),
                            'Рабочий']),
                            id='save_3min',
                            className="me-1"),
                    dbc.Button('Update', id='update',className="me-1", disabled=True),
                    dbc.Tooltip(
                        'Сохранить Фоновый Таймфрейм',
                        target='save_15min',
                        placement='bottom',
                        delay=tooltip_delay),
                    dbc.Tooltip(
                        'Сохранить Рабочий Таймфрейм',
                        target='save_3min',
                        placement='bottom',
                        delay=tooltip_delay),
                    dbc.Tooltip(
                        'Сохранить запись в базу данных',
                        target='update',
                        placement='bottom',
                        delay=tooltip_delay),
                ],
                    className='pt-2'),
            ],
            className='col-3'
        ),
        dbc.Col([
            dbc.Col([html.Div('Фоновый Таймфрейм'),html.Img(className='w-100',id='img15')]),
            dbc.Col([html.Div('Рабочий Таймфрейм'),html.Img(className='w-100',id='img3')])
        ]),
    ]),
    html.Div([
        dbc.NavLink(
            dbc.Button(
                html.I(className='bi bi-pie-chart-fill fs-3'),
                outline=False,
                className='btn btn-info',
                id='trade_statistic',
            ),
            href="/view_records",
        ),
        dbc.Tooltip(
            'Trade Statistic',
            target='trade_statistic',
            placement='left',
            delay=tooltip_delay),
        ],
        className='d-flex flex-column align-items-end fixed-bottom me-3 mb-3'
    ),
    ],
    className='p-3 mx-1'
    )



@callback(
    Output('ticker','invalid'),
    Output('img15', 'src'),
    Output('img3', 'src'),
    Output('img-alert','is_open'),
    Output('update','disabled'),
    Output('datefield','invalid'),
    Output('updated-alert','is_open'),
    Input('save_15min','n_clicks'),
    Input('save_3min','n_clicks'),
    Input('ticker', 'value'),
    Input('datefield','value'),
    Input('update','n_clicks'),
    State('checklist','value'),
    State('pnl_select','value'),
)
def get_img(n15, n3, ticker,date,updclk,checklist,pnl):
    global IMG15, IMG3, file_names
    trg_id = ctx.triggered_id

    if trg_id in ['save_15min','save_3min']:
        if not ticker:
            return True, IMG15, IMG3, False, True, False,False
        img  = get_img_clipboard()
        if not img:
            return False, IMG15, IMG3, True, True, False,False
        md5hash = hashlib.md5(img.tobytes()).hexdigest()

    if trg_id == 'save_15min':
        IMG15 = img
        fn = f'{ticker}_LT_{md5hash}.png'
        file_names['img15']=fn
    elif trg_id=='save_3min':
        IMG3 = img
        fn = f'{ticker}_ST_{md5hash}.png'
        file_names['img3']=fn
    elif trg_id=='ticker':
        return ticker in ['',None], IMG15,IMG3,False,True, False,False
    elif trg_id=='datefield':
        try:
            res = not bool(datetime.strptime(date, '%d.%m.%Y'))
        except ValueError:
            res = True
        return False, IMG15,IMG3,False,True, res,False
    elif trg_id == 'update':
        update_db(updclk,ticker,checklist,pnl)
        return False, IMG15, IMG3, False, True, False,True
    else:
        return False, IMG15, IMG3, False, True, False,False

    snapshot_folder = get_asset_url('snapshots')[1:]
    if not os.path.exists(snapshot_folder):
        os.mkdir(snapshot_folder)
    img.save(os.path.join(snapshot_folder,fn),'PNG')
    return False, IMG15, IMG3, False, not all(file_names.values()), False,False

def update_db(n_clicks,ticker,checklist,pnl):
    global DBNAME, features, file_names, IMG15, IMG3
    if not all(file_names.values()):
        return False
    if not os.path.exists(DBNAME):
        db = pd.DataFrame(columns=['ticker']+[f for f,v in features]+['filenames'])
    else:
        db = pd.read_csv(
            DBNAME,
            header=0,
            index_col=None,
            keep_default_na=False
        )
    last_cols = 2 #count_special_the_last_cols 
                  #2 because of PNL feature is not checkbox, Datetime is hidden
    chbx = [0]*(len(features)-last_cols)
    for i in checklist:
        chbx[i] = 1

    # check new features and add to db
    if len(features) != len(db.columns)-2:
        for nc in set([f for f,v in features])-set(db.columns):
            print('Adding column:',nc)
            db.insert(len(db.columns)-last_cols,nc,-1)

    new_row = [ticker]+chbx+[datetime.now().strftime('%d.%m.%Y'),pnl,list(file_names.values())]
    db.loc[len(db.index)]=new_row
    db.to_csv(DBNAME,index=False)
    for k in file_names:
        file_names[k] = ''

    IMG15 = None
    IMG3 = None
    return True


