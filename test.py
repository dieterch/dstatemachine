import math
import os
from collections.abc import Iterable
import dmyplant2 as dmp2

def flatten_list(l):
    """
    flatten by comprehension: [item for row in matrix for item in row]
    """
    matrix = [e if (isinstance(e,Iterable) and not isinstance(e, (str,bytes))) else [e] for e in l]
    return [item for row in matrix for item in row]

def dfigures(e = None):
    def fake_cyl(dataItem):
        return [dataItem[:-1] + '01',dataItem[:-1] + '02']
    func_cyl = fake_cyl if e is None else e.dataItemsCyl
    func_power = 5000 if e is None else math.ceil(e['Power_PowerNominal'] / 1000.0) * 1000.0 * 1.2
    f_figure = os.getcwd() + '/App/figures.json'
    figures = dmp2.load_json(f_figure)
    lfigures = figures.copy()
    for key in lfigures.keys():
        for i,r in enumerate(lfigures[key]):
            if 'ylim' in r:
                if r['ylim'] == "func_power":
                    figures[key][i]['ylim'] = [0,func_power]
            for j , dataitem in enumerate(r['col']):
                if 'func_cyl|' in dataitem:
                    lcol = figures[key][i]['col'].copy()
                    lcol[j] = func_cyl(f"{dataitem[len('func_cyl|'):]}")
                    figures[key][i]['col'] = flatten_list(lcol)
    return figures


def dfigures2(e = None):
    def fake_cyl(dataItem):
        return [dataItem[:-1] + '01',dataItem[:-1] + '02']
    func_cyl = fake_cyl if e is None else e.dataItemsCyl
    func_power = 5000 if e is None else math.ceil(e['Power_PowerNominal'] / 1000.0) * 1000.0 * 1.2
    f_figure = os.getcwd() + '/App/figures.json'
    figures = dmp2.load_json(f_figure)
    lfigures = figures.copy()
    for key in lfigures.keys():
        for i,r in enumerate(lfigures[key]):
            if 'ylim' in r:
                if r['ylim'] == "func_power":
                    figures[key][i]['ylim'] = [0,func_power]
            for j , dataitem in enumerate(r['col']):
                if 'func_cyl|' in dataitem:
                    lcol = figures[key][i]['col'].copy()
                    rlcol = func_cyl(f"{dataitem[len('func_cyl|'):]}")
                    lcol.remove(dataitem)
                    for item in rlcol[::-1]:
                        lcol.insert(j, item)
                    figures[key][i]['col'] = lcol
    return figures

def test(key,i):
    rawfigures = dmp2.load_json( os.getcwd() + '/App/figures.json')
    print(rawfigures[key][i])
    print(dfigures()[key][i])
    print(dfigures2()[key][i])

test('exhaust',-1)
a = [1, [99,100], 3]
print(flatten_list(a))