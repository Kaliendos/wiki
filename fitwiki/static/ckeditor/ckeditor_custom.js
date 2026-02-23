// Ждем загрузки CKEditor
CKEDITOR.on('instanceCreated', function(event) {
    var editor = event.editor;

    editor.on('dialogDefinition', function(ev) {
        var dialogName = ev.data.name;
        var dialogDefinition = ev.data.definition;

        // Модифицируем диалог ссылок
        if (dialogName === 'link') {
            var infoTab = dialogDefinition.getContents('info');

            // Добавляем поле для ID в расширенную вкладку
            var advancedTab = dialogDefinition.getContents('advanced');

            // Добавляем поле для ID в основную вкладку
            infoTab.add({
                type: 'text',
                id: 'linkId',
                label: 'ID элемента (якорь)',
                setup: function(data) {
                    this.setValue(data.linkId || '');
                },
                commit: function(data) {
                    data.linkId = this.getValue();
                }
            });

            // Добавляем поле для ID в расширенную вкладку
            advancedTab.add({
                type: 'text',
                id: 'elementId',
                label: 'ID элемента',
                setup: function(data) {
                    this.setValue(data.elementId || '');
                },
                commit: function(data) {
                    data.elementId = this.getValue();
                }
            });
        }

        // Модифицируем диалог якорей
        if (dialogName === 'anchor') {
            var anchorTab = dialogDefinition.getContents('info');
            var nameField = anchorTab.get('name');

            // Добавляем подсказку для формата ID
            if (nameField) {
                nameField.label = 'ID якоря (используйте латиницу и дефисы)';
                nameField.help = 'Например: vvedenie, osnovnaya-chast, zaklyuchenie';
            }
        }
    });
});

// Добавляем кастомную кнопку для вставки заголовка с ID
CKEDITOR.on('instanceReady', function(event) {
    var editor = event.editor;

    // Добавляем команду для вставки заголовка с ID
    editor.addCommand('insertHeadingWithId', {
        exec: function(editor) {
            var headingText = prompt('Введите текст заголовка:', '');
            if (headingText) {
                var id = headingText
                    .toLowerCase()
                    .replace(/[^a-zа-я0-9]+/g, '-')
                    .replace(/^-|-$/g, '');

                var headingHtml = '<h2 id="' + id + '">' + headingText + '</h2>';
                editor.insertHtml(headingHtml);
            }
        }
    });

    // Добавляем кнопку в тулбар
    editor.ui.addButton('InsertHeadingWithId', {
        label: 'Заголовок с ID',
        command: 'insertHeadingWithId',
        icon: 'https://ckeditor.com/docs/ckeditor4/4.16.2/examples/assets/placeholder.png',
        toolbar: 'insert'
    });
});