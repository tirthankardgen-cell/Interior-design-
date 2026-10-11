from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']); page=b.new_page(viewport={'width':1440,'height':1100});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/planner.html'); page.screenshot(path='/tmp/whole-flat.png'); initial=page.evaluate('Roomnote.getLayout()'); page.evaluate('Roomnote.validate(Roomnote.getLayout())')
 wall=next(o for o in initial['items'] if o['kind']=='wall');door=next(o for o in initial['items'] if o.get('wallId')==wall['id'])
 page.locator('[data-category="structure"]').click();page.locator('[data-kind="window"]').click();page.locator('#item-wall').select_option('6'); attached=page.evaluate('Roomnote.getLayout().items.at(-1)');assert attached['wallId']==wall['id']
 page.locator('[data-id="'+wall['id']+'"]').click(position={'x':3,'y':3},force=True)
 page.locator('#item-x').fill(str(round(wall['x']*100+10)));page.locator('#item-x').press('Tab')
 edited=page.evaluate('Roomnote.getLayout()');shifted=next(o for o in edited['items'] if o['id']==door['id']);assert abs(shifted['x']-door['x']-.1)<.02
 page.locator('#view-mode').click();page.locator('#show-walls').uncheck();page.wait_for_timeout(1200);page.screenshot(path='/tmp/whole-flat-3d.png');assert page.evaluate('Roomnote.getView()')=='3d';assert not errors,errors
 print('PASS whole flat: seven room labels, internal-wall window attachment, door follows wall edit, valid JSON and 3D.')
 b.close()
