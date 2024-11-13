from typing import Dict, List

scopes = {
    "Default" : "490ad6d1-69ab-43c3-931e-6827efdfbfd5",
    "Full Access" : "47f367d0-3290-4a8f-aaf2-15e2ee5658be",
    "No Access" : "05634f03-8dce-4f7a-9104-44300e9b639b",
    "Part Access" : "73fe5ade-a96e-4916-8be6-5bfae64a1c59"
}

def get_scope_id(scope : str) -> str:    
    return scopes[scope]


def get_scopes_id(scopes_list: List[str]) -> List[str]:
    return [scopes[scope] for scope in scopes_list]

def get_permissions_for_resource(permission : Dict[str,str], 
                                 resource_id : str, 
                                 user_id : int , 
                                 scope_key : str) -> bool:
    
    description = permission['description']
    resource, scope = description.split('_')
    
    name = permission['name']
    user, _ = name.split('_')
        
    return resource == resource_id and user_id == int(user) and scope in scope_key


def get_sub_resources(resource : Dict[str,str],
                      team_id : int,
                      parent_folder_id : str) -> bool:
    
    attributes = resource['attributes']
    parent_folder = attributes['parent_resource'][0]
    team = attributes['team'][0]
    
    return parent_folder == parent_folder_id and int(team) == team_id
    

def get_resource_by_team(resource : Dict[str,str],
                         team_id : int) -> bool:
    attributes = resource['attributes']
    return int(attributes['team'][0]) == team_id and attributes['parent_resource'][0] == 'None'


def get_resource_parent_resources(resources : List[Dict[str,str]],
                                   resource_id : str) -> List[str]:
    
    resource = list(filter(lambda res : res['_id'] == resource_id ,resources))
    
    if not resource:
        return [], []
    
    resource_parent_resource = resource[0]['attributes']['parent_resource'][0]
    
    
    resource_names = []
    resource_ids = []
    
    while resource_parent_resource != 'None':
        parent_resource = list(filter(lambda res : res['_id'] == resource_parent_resource,resources))
        resource_parent_resource = parent_resource[0]['attributes']['parent_resource'][0]
        resource_name = parent_resource[0]['name'].rsplit('/',1)
        resource_names.append(resource_name[1])
        resource_ids.append(parent_resource[0]['_id'])
    
    return resource_names,resource_ids


def get_sub_resources_to_delete(resources : List[Dict[str,str]], 
                               main_folder_id : str, 
                               resources_ids : List[str]) -> List[str]:
    
    sub_resources = list(filter(lambda resource : resource['attributes']['parent_resource'][0] == main_folder_id ,resources))
    
    resources_ids.extend([resource['_id'] for resource in sub_resources])
    
    for resource in sub_resources:
        get_sub_resources_to_delete(resources=resources,
                                    main_folder_id=resource['_id'],
                                    resources_ids=resources_ids)
        
    return resources_ids