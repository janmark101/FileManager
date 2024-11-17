export interface User{
    "id" : number,
    "username" : string,
    "first_name" : string,
    "last_name" : string,
    "email" : string,
    "token" : string
  }

export interface Team {
    "id" : number,
    "name" : string,
    "users" : User[],
    "created_at" : Date,
    "team_owner" : number,
    "adding_link_code" : string
  }

export interface Resource {
    "id" : string,
    "name" : string
  }


export interface ResourcePermissions {
    "user" : User,
    "permission" : string,
    "permission_id" : string,
    "permission_name" : string
  }
  
  
export interface File_{
    file : File,
    folder : string,
    name  : string,
    created_at : Date,
    updated_at : Date,
    file_extension : string
    id : number
  }


export interface Response{
    team : Team,
    resources : Resource[],
    files : File_[],
    resource_names : string[]
    resource_ids : string[]
  }


export interface ModalState {
  isAddResource: boolean;
  isRename: boolean;
  isManagePermission: boolean;
}


export function createDefaultModalState(): ModalState {
  return {
    isAddResource: false,
    isRename: false,
    isManagePermission: false,
  };
}


export interface DropDownState  {
  "add" : boolean,
  "resource" : boolean[]
}


export function createDefaultDropDownState() : DropDownState {
  return {
    add : false,
    resource : []
  }
}

export interface SubDropDownState extends DropDownState  {
  files : boolean[]
}


export interface PermissionsDataState  {
  "selectedPermission" : string,
  "permissions" : string[],
  "ResourcePermissions" : ResourcePermissions[],
  "ChangedResourcePermissions" : ResourcePermissions[]
}


export function createDefaultPermissionsData() : PermissionsDataState {
  return {
    selectedPermission : "Default",
    permissions : ["No Access", "Default", "Part Access" , "Full Access"],
    ResourcePermissions : [],
    ChangedResourcePermissions : []
  }
}
