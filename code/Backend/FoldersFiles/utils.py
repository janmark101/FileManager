from typing import Dict, List

scopes = {
    "Default" : "490ad6d1-69ab-43c3-931e-6827efdfbfd5",
    "Full Access" : "47f367d0-3290-4a8f-aaf2-15e2ee5658be",
    "No Access" : "05634f03-8dce-4f7a-9104-44300e9b639b",
    "Part Access" : "73fe5ade-a96e-4916-8be6-5bfae64a1c59"
}

scopes_id = {
    "490ad6d1-69ab-43c3-931e-6827efdfbfd5" : "Default",
    "47f367d0-3290-4a8f-aaf2-15e2ee5658be" : "Full Access",
    "05634f03-8dce-4f7a-9104-44300e9b639b" : "No Access",
    "73fe5ade-a96e-4916-8be6-5bfae64a1c59" : "Part Access"
}

def get_scope_id(scope : str) -> str:    
    return scopes[scope]

def get_scope_by_id(id: str) -> str:
    return scopes_id[id]


def get_scopes_id(scopes_list: List[str]) -> List[str]:
    return [scopes[scope] for scope in scopes_list]

def get_permissions_for_resource(permission : Dict[str,str], 
                                 resource_id : str, 
                                 user_id : int , 
                                 scope_key : str) -> bool:
    
    description = permission['description']
    resource, scope, _ = description.split('_')
    
    name = permission['name']
    user, _ = name.split('_')
        
    return resource == resource_id and user_id == int(user) and scope in scope_key


def get_sub_resources(resource : Dict[str,str],
                      team_id : int,
                      parent_resource_id : str) -> bool:
    """
    Function to get all sub resources for specific resource
    
    # Args :
        resource 
        team_id 
        parent_resource_id
        
        
    # Retrun :
        bool
    """
    
    attributes = resource['attributes']
    parent_resource = attributes['parent_resource'][0]
    team = attributes['team'][0]
    
    return parent_resource == parent_resource_id and int(team) == team_id
    

def get_resource_by_team(resource : Dict[str,str],
                         team_id : int) -> bool:
    """
    Function to get all resources for specific team and where parent_resources is none 
    
    # Args :
        resource 
        team_id 
        
        
    # Retrun :
        bool
    """
    attributes = resource['attributes']
    return int(attributes['team'][0]) == team_id and attributes['parent_resource'][0] == 'None'


def get_resource_parent_resources(resources : List[Dict[str,str]],
                                   resource_id : str) -> List[str]:
    """
    Function to get all parent resources for specific resource
    
    # Args :
        resources -> list of resources
        resource_id -> specific resource
        
        
    # Retrun :
        resource_names -> all parent resources names
        resource_ids -> all parent resources ids
    """
    
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
                               main_resource_id : str, 
                               resources_ids : List[str]) -> List[str]:
    """
    Function to get all sub resources for specific resource
    
    # Args :
        resource s -> list of resources
        main_resource_id -> specific resource
        resources_ids 
        
        
    # Retrun :
        resources_ids -> list contains ids resources to delete
    """
    
    sub_resources = list(filter(lambda resource : resource['attributes']['parent_resource'][0] == main_resource_id ,resources))
    
    resources_ids.extend([resource['_id'] for resource in sub_resources])
    
    for resource in sub_resources:
        get_sub_resources_to_delete(resources=resources,
                                    main_resource_id=resource['_id'],
                                    resources_ids=resources_ids)
        
    return resources_ids


    
    