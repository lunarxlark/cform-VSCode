import json
import re
import requests

url = {
    "ap-northeast-1" : "https://d33vqc0rt9ld30.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "ap-northeast-2" : "https://d1ane3fvebulky.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "ap-northeast-3" : "https://d2zq80gdmjim8k.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "ap-southeast-1" : "https://doigdx0kgq9el.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "ap-southeast-2" : "https://d2stg8d246z9di.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "ap-south-1" : "https://d2senuesg1djtx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "ca-central-1" : "https://d2s8ygphhesbe7.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "eu-central-1" : "https://d1mta8qj7i28i2.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "eu-north-1" : "https://diy8iv58sj6ba.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "eu-west-1" : "https://d3teyb21fexa9r.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "eu-west-2" : "https://d1742qcu2c1ncx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "eu-west-3" : "https://d2d0mfegowb3wk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "sa-east-1" : "https://d3c9jyj3w509b0.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "us-east-1" : "https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "us-east-2" : "https://dnwj8swjjbsbt.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "us-west-1" : "https://d68hl49wbnanq.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
    "us-west-2" : "https://d201a2mn26r7lk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
}

r = requests.get(url["us-east-1"])

o = open("./snippets/yaml-snippets.json", "w") 
cfn_def = r.json()
properties_json = cfn_def['PropertyTypes']
resources_json = cfn_def['ResourceTypes']
properties = [k for k, v in properties_json.items()]
resources = [k for k, v in resources_json.items()]

snippets = {}

# Template
snippets['template'] = {
    "prefix": "template",
    "body": [
        "AWSTemplateFormatVersion: \"2010-09-09\"",
        "Description: ${1:desc}",
        "Parameters:",
        "  ${2:param}",
        "Mappings:",
        "  ${3:map}",
        "Resources:",
        "  ${4:rsrc}",
        "Outputs:",
        "  ${5:out}"
    ],
    "scope": "source.cloudformation",
    "description": ""
}

# Resources
for r in resources:
    i = 1
    pattern = re.compile(r":+")
    body = []

    snippets[pattern.sub('-', r.lower())] = {
        'prefix'      : '',
        'body'        : [],
        'scope'       : '',
        'description' : ''
    }
    snippets[pattern.sub('-', r.lower())]['prefix'] = pattern.sub('-', r.lower())
    snippets[pattern.sub('-', r.lower())]['body'] = body
    snippets[pattern.sub('-', r.lower())]['scope'] = 'source.cloudformation'
    snippets[pattern.sub('-', r.lower())]['description'] = ''

    body.append("# " + resources_json[r]['Documentation'])
    body.append("${" + str(i) + ":my"+ pattern.sub('', r) +"}:")
    i+=1
    body.append("  Type: "+ r )
    body.append("  Properties:")


    for p, v in resources_json[r]['Properties'].items():
        if resources_json[r]['Properties'][p]['Required']:
            required_option = "(R)"
        else:
            required_option = "(O)"

        if resources_json[r]['Properties'][p].get('Type', '') in {'List', 'Map'}:

            if resources_json[r]['Properties'][p].get('ItemType', '') is not "":
                pattern1 = re.compile(r"\.*")
                pattern2 = re.compile(r":+")
                body.append("    " + p + " : [ ${" + str(i) + ":" + pattern2.sub('-', pattern1.sub('', r)).lower() + "." + resources_json[r]['Properties'][p]['ItemType'].lower() + required_option + "} ]")
            if resources_json[r]['Properties'][p].get('PrimitiveItemType', '') is not "":
                body.append("    " + p + " : [ ${" + str(i) + ":" + resources_json[r]['Properties'][p]['PrimitiveItemType'] + required_option + "} ]")
            elif resources_json[r]['Properties'][p].get('PrimitiveType', '') is not '':
                body.append("    " + p + " : [ ${" + str(i) + ":" + resources_json[r]['Properties'][p]['PrimitiveType'] + required_option + "} ]")

        elif resources_json[r]['Properties'][p].get('Type', '') == '':
            body.append("    " + p + " : ${" + str(i) + ":" + resources_json[r]['Properties'][p]['PrimitiveType'] + required_option + "}")
        else:
            a = resources_json[r]['Properties'][p].get('Type')
            body.append("    " + p + ": ${" + str(i) + ":" + pattern2.sub('-', r).lower() + "." + a.lower() + required_option + "}")

        i += 1

# Properties
for ps in properties:
    i = 1
    pattern = re.compile(r":+")
    body = []

    snippets[pattern.sub('-', ps.lower())] = {
        'prefix'      : '',
        'body'        : [],
        'scope'       : '',
        'description' : ''
    }
    snippets[pattern.sub('-', ps.lower())]['prefix'] = pattern.sub('-', ps.lower())
    snippets[pattern.sub('-', ps.lower())]['body'] = body
    snippets[pattern.sub('-', ps.lower())]['scope'] = 'source.cloudformation'
    snippets[pattern.sub('-', ps.lower())]['description'] = ''

    body.append("# " + properties_json[ps].get('Documentation', ''))
    #body.append("# " + properties_json[ps]['Documentation'])
    body.append("${" + str(i) + ":my"+ pattern.sub('', ps) +"}:")
    i+=1
    body.append("  Type: "+ ps )
    body.append("  Properties:")

    if properties_json[ps].get('Properties', '') != '':

        for p, v in properties_json[ps]['Properties'].items():

            required_option = ""
            if properties_json[ps]['Properties'][p]['Required']:
                required_option = "(R)"
            else:
                required_option = "(O)"

            if properties_json[ps]['Properties'][p].get('Type', '') in {'List', 'Map'}:
                if 'ItemType' in properties_json[ps]['Properties'][p]:
                    pattern1 = re.compile(r"\.*")
                    pattern2 = re.compile(r":+")
                    body.append("    " + p + " : [ ${" + str(i) + ":" + pattern2.sub('-', pattern1.sub('', ps)).lower() + "." + properties_json[ps]['Properties'][p]['ItemType'] + required_option + "} ]")
                elif 'PrimitiveItemType' in properties_json[ps]['Properties'][p]:
                    body.append("    " + p + " : [ ${" + str(i) + ":" + properties_json[ps]['Properties'][p]['PrimitiveItemType'] + required_option + "} ]")
                elif 'PrimitiveType' in properties_json[ps]['Properties'][p]:
                    body.append("    " + p + " : [ ${" + str(i) + ":" + properties_json[ps]['Properties'][p]['PrimitiveType'] + required_option + "} ]")

            elif properties_json[ps]['Properties'][p].get('Type', '') == '':
                body.append("    " + p + " : ${" + str(i) + ":" + properties_json[ps]['Properties'][p]['PrimitiveType'] + required_option + "}")
            else:
                pattern = re.compile(r"\.*")
                body.append("    " + p + " : ${" + str(i) + ":" + pattern2.sub('-', pattern1.sub('', ps)).lower() + "." + properties_json[ps]['Properties'][p]['Type'] + required_option + "}")

            i+=1


json.dump(snippets, o, ensure_ascii=False, indent=4, separators=(",", ":"))
