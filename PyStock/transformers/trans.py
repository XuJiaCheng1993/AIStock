"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-02-03 15:55
IDE: PyCharm
Introduction:
"""
import talib
import pandas as pd
import numpy as np
from itertools import product, chain



class innerFunction():
    def __init__(self, name, func, inputs, params, outputs):
        self.__name = name
        self.__exec = func
        self.__inputs = inputs

        combs = self.__combs(params)
        self.__params_combs = combs

        output_name, output_num = self.__outputs(outputs)
        self.__output_name = output_name
        self.__output_num = output_num

    def __combs(self, params):
        n, p = [], []
        for k, v in params.items():
            if isinstance(v, (tuple, list)):
                p.append(range(*v))
            elif isinstance(v, set):
                p.append(list(v))
            else:
                p.append([v, ])
            n.append(k)

        return [{j:v[i] for i, j in enumerate(n)} for v in product(*p) ]

    def __outputs(self, outputs):
        suffix = ['_'.join([f'{k.upper()}{v}' for k, v in ii.items()]) for ii in self.param_combs ]
        if not outputs:
            outputs = (self.name, )
        output_name = [[f'{ot.upper()}_{suf}' for ot in outputs] for suf in suffix]
        output_num = 1 if not outputs else len(outputs)
        return output_name, output_num


    def exec(self, *args, **kwargs):
        return self.__exec(*args, **kwargs)

    @property
    def name(self):
        return self.__name

    @property
    def inputs(self):
        return self.__inputs

    @property
    def param_combs(self):
        return self.__params_combs

    @property
    def output_name(self):
        return self.__output_name

    @property
    def output_num(self):
        return self.__output_num


class Transformer(object):
    inputs = ('open', 'high', 'low', 'close', 'volume')
    params = {'timeperiod':(5, 90, 10),
              'SMA__timeperiod':14}
    funcs = (('SMA', 'talib.SMA', (-1,), ('timeperiod',), ()), )


    def __parse_funcs(self):
        ''' 解析函数'''
        for (fn, fc, fi, fp, fo) in self.funcs:
            params = {}
            for fpp in fp:
                if f'{fn}__{fpp}' in self.params.keys():
                    fp_det = self.params[f'{fn}__{fpp}']
                else:
                    fp_det = self.params[fpp]
                params.update({fpp:fp_det})

            inputs = [self.inputs[f] if f >= 0 else 'any' for f in fi]

            exec(f'self.{fn}=innerFunction(name="{fn}", func={fc}, inputs={inputs}, params={params}, outputs={fo})')


    def set_params(self, params={}):
        ''' 设置函数的参数'''
        for k, v in params.items():
            self.params.update({k:v})
        self.__parse_funcs()
        return self


    def __init__(self, funcs=None, params=None, *args, **kwargs):
        if funcs is not None:
            self.funcs = [f for f in self.funcs if f[0] in funcs]

        if params is None:
            self.__parse_funcs()
        else:
            self.set_params(params)


    def transform(self, open=None, high=None, low=None, close=None, volume=None, any_map='close', *args, **kwargs):
        kwargs.update(dict(open=open, high=high, low=low, close=close, volume=volume))
        kwargs.update({'any':kwargs[any_map]})

        columns_name = []
        for fc in self.funcs:
            columns_name += list(chain.from_iterable(eval(f'self.{fc[0]}.output_name')))

        X = pd.DataFrame(index=range(len(close)), columns=columns_name)
        for fc in self.funcs:
            inputs = [kwargs[ip] for ip in eval(f'self.{fc[0]}.inputs')]
            output_num = eval(f'self.{fc[0]}.output_num')
            for fn, fp in zip(eval(f'self.{fc[0]}.output_name'), eval(f'self.{fc[0]}.param_combs')):
                tmp = eval(f'self.{fc[0]}.exec')(*inputs, **fp)
                if output_num <= 1:
                    X[fn[0]] = tmp
                else:
                    for i, ffn in enumerate(fn):
                        X[ffn] = tmp[i]
        return X.fillna(method='bfill')



class OverlapTransformer(Transformer):
    params = {'BBANDS__timeperiod':5, 'nbdevup':2, 'nbdevdn':2, 'matype':0, 'timeperiod':30, 'fastlimit':0.5,
              'slowlimit':0.05, 'acceleration':0.02, 'maximum':0.2, 'startvalue': 0, 'accelerationinitlong': 0.02,
              'accelerationlong': 0.02, 'accelerationmaxlong': 0.2, 'accelerationinitshort': 0.02,
              'accelerationshort': 0.02, 'accelerationmaxshort': 0.2, 'T3__timeperiod': 5, 'vfactor': 0.7,
              'MIDPOINT__timeperiod':14, 'MIDPRICE__timeperiod':14}

    funcs = (('BBANDS', 'talib.BBANDS', (-1, ), ('timeperiod', 'nbdevup', 'nbdevdn', 'matype'), ('upbband', 'midbband', 'lowbband')),
             ('DEMA', 'talib.DEMA', (-1, ), ('timeperiod', ), ()),
             ('HTTRENDLINE', 'talib.HT_TRENDLINE', (-1, ), (), ()),
             ('KAMA', 'talib.KAMA', (-1, ), ('timeperiod', ), ()),
             ('MAMA', 'talib.MAMA', (-1, ), ('fastlimit', 'slowlimit'), ('mama', 'fama')),
             ('MIDPOINT', 'talib.MIDPOINT', (-1, ), ('timeperiod', ), ()),
             ('MIDPRICE', 'talib.MIDPRICE', (1, 2), ('timeperiod', ), ()),
             ('SAR', 'talib.SAR', (1, 2), ('acceleration', 'maximum'), ()),
             ('SAREXT', 'talib.SAREXT', (1, 2), ('startvalue', 'accelerationinitlong', 'accelerationlong',
                                               'accelerationmaxlong', 'accelerationmaxlong', 'accelerationinitshort',
                                               'accelerationshort', 'accelerationmaxshort'), ()),
             ('SMA', 'talib.SMA', (-1, ), ('timeperiod', ), ()),
             ('T3', 'talib.T3', (-1, ), ('timeperiod', 'vfactor'), ()),
             ('TEMA', 'talib.TEMA', (-1, ), ('timeperiod', ), ()),
             ('TRIMA', 'talib.TRIMA', (-1, ), ('timeperiod', ), ()),
             ('WMA', 'talib.WMA', (-1, ), ('timeperiod', ), ()),
             )

    def __init__(self, *args, **kwargs):
        super(OverlapTransformer, self).__init__(*args, **kwargs)


class MomentumTransformer(Transformer):
    params = {'timeperiod':14, 'fastperiod':12, 'slowperiod':26, 'matype':0, 'fastmatype':0, 'slowmatype':0,
              'signalperiod':9, 'signalmatype':0, 'fastk_period':5, 'fastd_period':5, 'fastd_matype':0,
              'slowk_period':3, 'slowk_matype':0, 'slowd_period':3, 'slowd_matype':0, 'TRIX__timeperiod':30,
              'timeperiod1':7, 'timeperiod2':14, 'timeperiod3':28}

    funcs = (('ADX', 'talib.ADX', (1, 2, 3), ('timeperiod', ), () ),
             ('ADXR', 'talib.ADXR', (1, 2, 3), ('timeperiod', ), ()),
             ('APO', 'talib.APO', (-1, ), ('fastperiod', 'slowperiod', 'matype'), ()),
             ('AROON', 'talib.AROON', (1, 2), ('timeperiod', ), ('aroondown', 'aroonup',)),
             ('AROONOSC', 'talib.AROONOSC', (1, 2), ('timeperiod', ), ()),
             ('BOP', 'talib.BOP', (0, 1, 2, 3), (), ()),
             ('CCI', 'talib.CCI', (1, 2, 3), ('timeperiod',), ()),
             ('CMO', 'talib.CMO', (-1, ), ('timeperiod',), ()),
             ('DX', 'talib.DX', (1, 2, 3 ), ('timeperiod',), ()),
             ('MACDEXT', 'talib.MACDEXT', (-1, ), ('fastperiod', 'fastmatype', 'slowperiod', 'slowmatype',
                                                    'signalperiod', 'signalmatype'), ('macd', 'macdsignal', 'macdhist')),
             ('MFI', 'talib.MFI', (1, 2, 3, 4), ('timeperiod',), ()),
             ('MINUSDI', 'talib.MINUS_DI', (1, 2, 3), ('timeperiod',), ()),
             ('MINUSDM', 'talib.MINUS_DM', (1, 2), ('timeperiod',), ()),
             ('MOM', 'talib.MOM', (-1, ), ('timeperiod',), ()),
             ('PLUSDI', 'talib.PLUS_DI', (1, 2, 3), ('timeperiod',), ()),
             ('PLUSDM', 'talib.PLUS_DM', (1, 2), ('timeperiod',), ()),
             ('PPO', 'talib.PPO', (-1, ), ('fastperiod', 'slowperiod', 'matype'), ()),
             ('ROC', 'talib.ROC', (-1, ), ('timeperiod',), ()),
             ('ROCP', 'talib.ROCP', (-1, ), ('timeperiod',), ()),
             ('ROCR', 'talib.ROCR', (-1, ), ('timeperiod',), ()),
             ('RSI', 'talib.RSI', (-1, ), ('timeperiod',), ()),

             ('STOCH', 'talib.STOCH', (1, 2, 3), ('fastk_period', 'slowk_period', 'slowk_matype', 'slowd_period',
                                                'slowd_matype'), ('slowk', 'slowd')),
             ('STOCHF', 'talib.STOCHF', (1, 2, 3), ('fastk_period', 'fastd_period', 'fastd_matype'), ('fastk', 'fastd')),
             ('STOCHRSI', 'talib.STOCHRSI', (-1, ), ('timeperiod', 'fastk_period', 'fastd_period', 'fastd_matype'),
                         ('fastkrsi', 'fastdrsi')),

             ('TRIX', 'talib.TRIX', (-1, ), ('timeperiod',), ()),
             ('ULTOSC', 'talib.ULTOSC', (1, 2, 3), ('timeperiod1', 'timeperiod2', 'timeperiod3'), ()),
             ('WILLR', 'talib.WILLR', (1, 2, 3), ('timeperiod',), ()),
             )


    def __init__(self,  *args, **kwargs):
        super(MomentumTransformer, self).__init__(*args, **kwargs)



class VolumeTransformer(Transformer):
    params = {'fastperiod':3, 'slowperiod':10}

    funcs = (('AD', 'talib.AD', (1, 2, 3, 4), (), ()),
             ('ADOSC', 'talib.ADOSC', (1, 2, 3, 4), ('fastperiod', 'slowperiod'), ()),
             ('OBV', 'talib.OBV', (3, 4), (), ()),
             )

    def __init__(self, *args, **kwargs):
        super(VolumeTransformer, self).__init__(*args, **kwargs)



class VolatilityTransformer(Transformer):
    params = {'timeperiod':14}

    funcs = (('ATR', 'talib.ATR', (1, 2, 3), ('timeperiod'), ()),
             ('NATR', 'talib.NATR', (1, 2, 3), ('timeperiod'), ()),
             ('TRANGE', 'talib.TRANGE', (1, 2, 3), (), ()),
             )

    def __init__(self, *args, **kwargs):
        super(VolatilityTransformer, self).__init__(*args, **kwargs)


class CycleTransformer(Transformer):
    funcs = (('HTDCPERIOD', talib.HT_DCPERIOD, (-1, ), (), ()),
             ('HTDCPHASE', talib.HT_DCPHASE, (-1,), (), ()),
             ('HTPHASOR', talib.HT_PHASOR, (-1,), (), ()),
             ('HTSINE', talib.HT_SINE, (-1,), (), ()),
             ('HTTRENDMODE', talib.HT_TRENDMODE, (-1,), (), ()),
             )

    def __init__(self, *args, **kwargs):
        super(CycleTransformer, self).__init__(*args, **kwargs)



































