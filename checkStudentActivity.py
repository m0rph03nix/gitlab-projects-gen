#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Raphaël LEBER"

import gitlab
import yaml
import re
import sys
import time

class CheckStudentActivity:

    """
    Check student commits
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


        early = 'T00:00:00+02:00Z'
        late = 'T23:59:00+02:00Z'

        # slot SAT IRC 2020
        slots_official = ["2022-04-05", "2022-04-06", "2022-04-08", "2022-04-25", "2022-04-26" ]
        slots = ["2022-04-05", "2022-04-06", "2022-04-07", "2022-04-08", "2022-04-25", "2022-04-26" ] #["2021-04-14","2021-04-15","2021-04-16","2021-04-17","2021-04-18","2021-04-19","2021-04-20","2021-04-21","2021-04-22","2021-04-23","2021-04-24","2021-04-25","2021-04-26","2021-04-27","2021-04-28","2021-04-29","2021-04-30"]

                            



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
                self.group_id = self.gl.groups.create({'name': self.module_name, 'path': self.module_name}).id            
            else:
                self.group_id = grp[0].id                

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
                    #self.prj_name = "S" + re.findall('\d+',topic_item)[0]
                    
                    #if option != '--only-group-number':
                    #    self.prj_name = "S" + re.findall('\d+',topic_item)[0]
                    #    self.prj_name = self.prj_name + '_G' + re.findall('\d+',team_item)[0]
                    #else:
                    self.prj_name = 'G' + re.findall('\d+',team_item)[0]

                    for nom in self.team_content:
                        #print("\t\t" + nom[0])
                        self.prj_name = self.prj_name + '_' + nom[0]

                    print('\n# ', self.prj_name)                    

                    
                    group = self.gl.groups.get( self.group_id )
                    subgroups = group.subgroups.list()
                    
                    sub_grp = self.gl.groups.list(search=self.topic_group_name[topic_idx-1])


                    sub_group_id = sub_grp[0].id

                    projects = self.gl.projects.list(search=self.prj_name, namespace_id=sub_group_id)

                    project = projects[0]
                    #print(project)
   








                    for slot in slots:
                        if slot in slots_official:
                            print("### Commits the {0}".format(slot.replace('-',' ')))
                        commits = project.commits.list(query_parameters={'all':'True','since': slot+early, 'until': slot+late })                        
                        #commits = project.commits.list(all = True)  
                        
                      
                        #print(commits)
                        if len(commits) > 0:
                            if slot not in slots_official:
                                print("### Commits the {0} - during student free time :)".format(slot.replace('-',' ')))
                            for commit in reversed(commits):
                                #print(commit)
                                title = commit.title
                                author = commit.author_email
                                print(author + " : " + title + "  " )
                        #print("\n")
                    
                    print("### TAGS: ")
                    tags = project.tags.list()
                    for tag in tags:
                        #print(project.http_url_to_repo)
                        print("- {0} : [{1}]({2}/-/tree/{1} )  ".format(tag.commit['created_at'].replace('T',' ')[:-13], tag.name, project.http_url_to_repo.replace('.git','')))
                        #print(tag.commit['created_at'])
                        
                        

                    print("\n\n.   ")




                           
                    # commits = project.commits.list(query_parameters={'all':'True','since': '2020-04-09T00:00:00+02:00Z'}) #since='2020-04-01 00:00:00+02:00', until='2020-04-02 18:30:00+02:00')
                    # #print(commits)
                    # if len(commits) > 0:
                    #     for commit in reversed(commits):
                    #         #print(commit)
                    #         title = commit.title
                    #         author = commit.author_email
                    #         print(author + " : " + title )
                            
                    """
                    for person in self.team_content:
                        ids = self.gl.users.list(search=person[2])
                        if len(ids) > 0:
                            member = project.members.create({'user_id': ids[0].id , 'access_level': gitlab.MAINTAINER_ACCESS})
                    """
                   


if __name__ == "__main__":
    csa = CheckStudentActivity()

