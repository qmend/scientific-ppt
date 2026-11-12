"""Isolated Office worker. Called by rendering.py with a hard process timeout."""
import json
from pathlib import Path
import sys


def office(source,output):
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    app=win32com.client.DispatchEx('PowerPoint.Application')
    initial=app.Presentations.Count
    old_security=app.AutomationSecurity
    app.AutomationSecurity=3
    app.DisplayAlerts=1
    pres=None
    try:
        pres=app.Presentations.Open(str(Path(source).resolve()),True,False,False)
        metrics=[]
        for i in range(1,pres.Slides.Count+1):
            slide=pres.Slides(i)
            for j in range(1,slide.Shapes.Count+1):
                shape=slide.Shapes(j)
                if shape.HasTextFrame and shape.TextFrame.HasText:
                    tf=shape.TextFrame2;tr=tf.TextRange
                    metrics.append({'page':i,'shape':j,'name':shape.Name,'text':tr.Text,
                        'bound_height':tr.BoundHeight,'bound_width':tr.BoundWidth,
                        'available_height':shape.Height-tf.MarginTop-tf.MarginBottom,
                        'available_width':shape.Width-tf.MarginLeft-tf.MarginRight})
                if shape.HasTable:
                    for r in range(1,shape.Table.Rows.Count+1):
                        for c in range(1,shape.Table.Columns.Count+1):
                            cell=shape.Table.Cell(r,c).Shape;tf=cell.TextFrame2;tr=tf.TextRange
                            metrics.append({'page':i,'shape':j,'name':f'table:{r}:{c}','text':tr.Text,
                                'bound_height':tr.BoundHeight,'bound_width':tr.BoundWidth,
                                'available_height':cell.Height-tf.MarginTop-tf.MarginBottom,
                                'available_width':cell.Width-tf.MarginLeft-tf.MarginRight})
        pres.SaveAs(str(Path(output).resolve()),24 if Path(output).suffix.lower()=='.pptx' else 32)
        Path(output).with_suffix('.metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    finally:
        if pres is not None:pres.Close()
        app.AutomationSecurity=old_security
        if initial==0 and app.Presentations.Count==0:app.Quit()
        pythoncom.CoUninitialize()


if __name__=='__main__':office(sys.argv[1],sys.argv[2])
