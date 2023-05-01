locals {

  tag_defaults = {
    Owner   = "chisel"
    Product = "botc-custom-script-json2pdf"
    InfoURL = "https://github.com/chizmw/botc-custom-script-json2pdf"
  }

  # wkspc_site_name is based on the workspace name; if it's 'prod' we use 'make', if it's 'dev' we use 'preview'
  wkspc_site_name = {
    prod = "maker"
    dev  = "preview"
  }

  # get the lookup value from the wkspc_site_name map based on the workspace name
  site_name = lookup(local.wkspc_site_name, terraform.workspace)
}
