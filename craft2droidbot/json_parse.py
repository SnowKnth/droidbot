import re
import json

def convert_json(input):
    views = {}
    states = {}
    operations = {}
    main = {}

    
    with open(input, 'r') as f:
        input_json = json.load(f)

    cur_activity = None
    state_name = None
    operation_name = None
    view_name = None
    operation = None
    state_n = 0
    new_state = 1
    oracle_seen = 0

    for index, item in enumerate(input_json):
        if item['action'][0] not in ['click', 'wait_until_element_presence', 'send_keys_and_enter', 'wait_until_text_presence', 'send_keys_and_hide_keyboard', 'wait_until_text_invisible', 'clear_and_send_keys', 'send_keys', 'clear_and_send_keys_and_hide_keyboard',"long_press", "swipe_right", "swipe_left", "KEY_BACK"]:
            print(item['action'][0] + " file:" + input)
            continue
    
        if(item['event_type'] == 'SYS_EVENT' and item['action'][0] == 'KEY_BACK'):
            operation = {
                "event_type": "key",
                "name": item['action'][0].split('_')[1].upper()
            }
            operations[operation_name].append(operation)
            if(index == len(input_json) - 1):
                operation = {
                    "event_type": "exit"
                }
                operations[operation_name].append(operation)
            continue
        #新的activity出现
        if item['activity'].lower().replace('.', '_') != cur_activity:
            cur_activity = item['activity'].replace('.', '_')

        #   swipe_right  long_press KEY_BACK
        # if item['event_type'] != 'oracle':      
        #识别是否是新的view,是的话则在views中记录和当前states中记录
        view_name = item['resource-id'].split('/')[-1] + '_rid_' + re.sub(r'\W+', '_', item['content-desc'].lower())+ 'c_desc'+ re.sub(r'\W+', '_', item['class'].split('.')[-1].lower())+ '_class_'+ re.sub(r'\W+', '_', item['text'])+ '_text'
        view_name.replace("(wrong)","")
        if view_name not in views:
            # 初始化一个空字典来存放view  
            view = {}                
            # 根据条件添加resource_id字段  
            if item.get('resource-id')and item['resource-id'] != '':  
                view["resource_id"] = ".*" + item['resource-id'].split('.')[-1].split(r'/')[-1]               
            # 根据条件添加class字段  
            if item.get('class')and item['class'] != '':  
                view["class"] = ".*" + item['class'].split('.')[-1]                
            # 根据条件添加content_desc字段，只有当content_desc不为空字符串时才添加  
            if item.get('content-desc') and item['content-desc'] != '':  
                view["content_desc"] = ".*" + item['content-desc'].split('.')[-1]  
            # if item.get('text') and item['text'] != '':  
            #     view["text"] = item['text'] 
            views[view_name] = view
            
             
        state_n += 1 
        state_name = cur_activity + '_state' + str(state_n)
        operation_name = cur_activity + "_operation" + str(state_n)
        states[state_name]={"activity": ".*" + item['activity'].split('.')[-1],"views":[]}
        operations[operation_name]=[]         
        states[state_name]['views'].append(view_name)
        main[state_name] = [operation_name] 
            
            
        #记录operation信息    
        if(item['event_type'] == 'gui' and item['action'][0] in ['send_keys_and_enter', 'clear_and_send_keys', 'clear_and_send_keys_and_hide_keyboard', 'send_keys', 'send_keys_and_hide_keyboard']) :
            operation = {
                "event_type": "set_text",
                "target_view": view_name,
                "text": item['action'][1]
            }
            # if(item['action'][0] in ['send_keys_and_hide_keyboard','clear_and_send_keys_and_hide_keyboard']):
            #     operations[operation_name].append(operation)
            #     operation = {
            #         "event_type": "key",
            #         "name": "BACK"
            #     }
            if(item['action'][0] == 'send_keys_and_enter'):
                operations[operation_name].append(operation)
                operation = {
                    "event_type": "key",
                    "name": "ENTER"
                }
            
            if(index == len(input_json) - 1):
                operation = {
                    "event_type": "exit"
                }
                operations[operation_name].append(operation)
        elif(item['event_type'] == 'gui' and item['action'][0] == 'click'):
            operation = {
                "event_type": "click",
                "target_view": view_name,
            }
        elif(item['event_type'] == 'gui' and item['action'][0] == 'long_press'):
            operation = {
                "event_type": "long_click",
                "target_view": view_name,
            }
        elif(item['event_type'] == 'gui' and item['action'][0] in ['swipe_right', 'swipe_left']):
            operation = {
                "event_type": "scroll",
                "target_view": view_name,
                "direction": item['action'][0].split('_')[1].upper()
            }
        elif(item['event_type'] == 'oracle' and item['action'][0] in ['wait_until_text_presence', 'wait_until_text_invisible']) :
            operation = {
                "event_type": "oracle",
                "target_view":view_name,
                "condition": item['action'][0],
                "sleep_t": item['action'][1],
                "assert_text": item['action'][3]
            }
        elif(item['event_type'] == 'oracle' and item['action'][0] in ['wait_until_element_presence']):
            operation = {
                "event_type": "oracle",
                "target_view":view_name,
                "condition": item['action'][0],
                "sleep_t": item['action'][1]
            }
                  
        operations[operation_name].append(operation)
        if(index == len(input_json) - 1):
            operation = {
                "event_type": "exit"
            }
            operations[operation_name].append(operation)          

    result = {
        "views": views,
        "states": states,
        "operations": operations,
        "main": main
    }

    return result


# Convert JSON
for category in ['a1', 'a2', 'a3', 'a4', 'a5']:
    cg_index =  category[1]
    for i in range(1,3):
        b_index = 'b'+cg_index+str(i)
        for j in range(1,6):
            app_json = 'a'+cg_index+str(j)
            outputfile = "./craft2droidbot/test_repo/"+category+"/"+b_index+"/base/"+app_json+"_drb.json"
            converted_json = convert_json("./craft2droidbot/test_repo/"+category+"/"+b_index+"/base/"+app_json+".json")
            with open(outputfile, 'w') as fout:
                json.dump(converted_json, fout, indent=4)
# Print converted JSON
# print(json.dumps(converted_json, indent=4))
