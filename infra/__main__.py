import pulumi
import pulumi_aws as aws

lmgify_net_zone = aws.route53.Zone(
    "lmgify-net-zone",
    comment="HostedZone created by Route53 Registrar",
    name="lmgify.net",
    opts=pulumi.ResourceOptions(protect=True),
)

pulumi.export('zone_id', lmgify_net_zone.id)

site_s3_bucket = aws.s3.Bucket("lmgify-net")
