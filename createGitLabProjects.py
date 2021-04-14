#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Raphaël LEBER"

import gitlab
import yaml
import re
import sys
import time

class ProjectsGenerator:

    """
    Creates groups and projects on GitLab, thanks to teams and topics YAML files
    """    

    def __init__(self):

        if len(sys.argv) > 1:
            teams_filename = sys.argv[1]
        else:
            teams_filename = 'teams.yaml'         


        if len(sys.argv) > 2:
            topics_filename = sys.argv[2]
        else:
            topics_filename = 'topics.yaml'  
               

        if len(sys.argv) > 3:
            option = sys.argv[3]
        else:
            option = ''               


        # Get tocken to access gitlab account
        with open('token.yaml') as file:
            token = yaml.load(file, Loader=yaml.FullLoader)
            self.token = token['token_gitlab']

        self.gl = gitlab.Gitlab('https://gitlab.com', private_token=self.token)



        # Open topics description file
        with open(topics_filename) as file:
            topics = yaml.load(file, Loader=yaml.FullLoader)
            print(topics)

            self.module_name = list(topics.keys())[0]
            #print(self.module_name)

            grp = self.gl.groups.list(search=self.module_name)
            if len( grp )==0 :
                print( self.module_name )
                print( self.module_name )
                self.group_id = self.gl.groups.create({'name': self.module_name, 'path': self.module_name}).id            
            else:
                self.group_id = grp[0].id

            for i in range(len( grp )):
                print( "\n--GRP--" ) 
                print( grp[i] ) 
                print( grp[i].id )      
        

            #quit()
            #time.sleep(1)                

            topic_list = topics.keys()

            self.topic_group_name = []
            self.topic_description = []

            for topic_key, topic in topics[self.module_name].items() :

                print( topic_key+'__'+topic["name"].replace(' ','_') )
                self.topic_group_name.append( topic_key+'__'+topic["name"].replace(' ','_')) 
                self.topic_description.append( '[' + topic["description"] + '](' + topic["url"] + ')'  )


        with open(teams_filename) as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            teams = yaml.load(file, Loader=yaml.FullLoader)

            # sort_teams = yaml.dump(teams, sort_keys=True)

            #print(teams)

            for topic_item, self.topic_content in teams.items():
                #print(topic_item, ":")
                

                for team_item, self.team_content in self.topic_content.items():


                    # Set project name with this format : Sx_Gy_NAME1_NAME2_NAME..._NAMEn with s the topic number and y the team number
                    #print("\t" + team_item)
                    topic_idx = int(re.findall('\d+',topic_item)[0])

                    if option != '--only-group-number':
                        self.prj_name = "S" + re.findall('\d+',topic_item)[0]
                        self.prj_name = self.prj_name + '_G' + re.findall('\d+',team_item)[0]
                    else:
                        self.prj_name = 'G' + re.findall('\d+',team_item)[0]

                    for nom in self.team_content:
                        #print("\t\t" + nom[0])
                        self.prj_name = self.prj_name + '_' + nom[0].replace('\xa0','')

                    print(self.prj_name)                    

                    
                    group = self.gl.groups.get( self.group_id )
                    subgroups = group.subgroups.list()


                    sub_grp = self.gl.groups.list(search=self.topic_group_name[topic_idx-1])

                    sgroup_exists = False
                    sgroup_it = 0

                    for i in range(len( sub_grp )):
                        if( sub_grp[i].full_path == self.module_name.lower() + '/' + self.topic_group_name[topic_idx-1] ) :
                            sgroup_exists = True
                            sgroup_it = i

                    if sgroup_exists == False :
                        sub_group_id = self.gl.groups.create({'name': self.topic_group_name[topic_idx-1], 'path': self.topic_group_name[topic_idx-1], 'parent_id' : self.group_id } ).id
                    else:
                        sub_group_id = sub_grp[sgroup_it].id

                    #print ("subgroup_id : ", sub_group_id  )

                    #time.sleep(1)

                    projects = self.gl.projects.list(search=self.prj_name, namespace_id=sub_group_id)

                    if len(projects)==0 :
                        project = self.gl.projects.create({'name': self.prj_name, 'namespace_id': sub_group_id, 'description':  self.topic_description[topic_idx-1] } )

                    else:
                        project = projects[0]
   
                    
                    for person in self.team_content:
                        ids = self.gl.users.list(search=person[2])
                        if len(ids) > 0:
                            member = project.members.create({'user_id': ids[0].id , 'access_level': gitlab.MAINTAINER_ACCESS})

                   


if __name__ == "__main__":
    pg = ProjectsGenerator()

