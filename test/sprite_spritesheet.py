from src.sprite import SpriteSheet

sheet = SpriteSheet('Default Button.png', 3, 1)
print(f'Lookup before naming: {sheet.lookup}')
sheet.name('Unpressed', 'Hover', 'Pressed')
print(f'Lookup after naming: {sheet.lookup}')
print(f'Single item: {sheet.item_dim}')
print(f'Cols: {sheet.cols}, Rows: {sheet.rows}')
print(f'Total Dim: {sheet.img.width}, {sheet.img.height}')
