from typing import Dict, List
scopes = {
    "default" : "490ad6d1-69ab-43c3-931e-6827efdfbfd5",
    "full_access" : "47f367d0-3290-4a8f-aaf2-15e2ee5658be",
    "no_access" : "05634f03-8dce-4f7a-9104-44300e9b639b",
    "part_access" : "73fe5ade-a96e-4916-8be6-5bfae64a1c59"
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
    
    print(scope,scope_key)
        
    return resource == resource_id and user_id == int(user) and scope in scope_key