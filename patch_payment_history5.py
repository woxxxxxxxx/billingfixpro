with open('tools/payment-history.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_printdoc = """function printDoc(){
  var o=document.getElementById('output');
  if(!o||o.style.display==='none'||o.style.display===''){
    alert('Please click Generate Payment History first, then print.');
    return;
  }
  window.print();
}"""

new_printdoc = r"""function printDoc(){
  var preview=document.getElementById('preview');
  if(!preview||!preview.innerHTML.trim()){
    alert('Please click Generate Payment History first, then print.');
    return;
  }
  var w=window.open('','_blank','width=900,height=700');
  w.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Payment History</title>'
    +'<style>body{font-family:Helvetica Neue,Arial,sans-serif;margin:0;padding:20px;background:#fff}'
    +'@media print{body{padding:0}}</style></head>'
    +'<body>'+preview.innerHTML+'<script>window.onload=function(){window.print();window.onafterprint=function(){window.close();};}<\/script>'
    +'</body></html>');
  w.document.close();
}"""

if old_printdoc in content:
    content = content.replace(old_printdoc, new_printdoc)
    print("printDoc replaced OK")
else:
    print("ERROR: old_printdoc not found")
    idx = content.find('function printDoc()')
    print(repr(content[idx:idx+200]))

with open('tools/payment-history.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
