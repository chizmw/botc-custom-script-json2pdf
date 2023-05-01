# data lookup for the zone_id
data "aws_route53_zone" "velvetlookout_org" {
  name         = var.domain_name
  private_zone = false
}

locals {
  MXRecordSets = {
    "" = {
      Type = "MX",
      TTL  = 3600,
      MXRecords = [
        {
          "Value" = "10 mx1.forwardemail.net"
        },
        {
          "Value" = "20 mx1.forwardemail.net"
        }
      ]
    }
  }
}

resource "aws_route53_record" "mx_records" {
  for_each = local.MXRecordSets
  zone_id  = data.aws_route53_zone.velvetlookout_org.id
  name     = each.key
  type     = each.value.Type
  records  = [for key, record in each.value["MXRecords"] : record["Value"]]
  ttl      = each.value.TTL
}

# add a TXT record for domain to verify ownership
resource "aws_route53_record" "txt-forwardmail" {
  zone_id = data.aws_route53_zone.velvetlookout_org.zone_id
  name    = ""
  type    = "TXT"
  ttl     = "3600"
  records = ["forward-email=chisel@malik-wright.uk"]
}
