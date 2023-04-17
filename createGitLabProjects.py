#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Raphaël LEBER"

import gitlab
import yaml
import re
import sys
import time
from copy import deepcopy
import copy

class ProjectsGenerator:

    """
    Creates groups and projects on GitLab, thanks to teams and topics YAML files
    """    

    def __init__(self):


        # self.loadings()
        # self.create_main_path()
        # self.create_topics()
        # self.create_projects()

        pass

    def loadings(self):
        """
        Loads yaml files : tocken, teams (groups) and topics
        Init main class attributes
        """            

        if len(sys.argv) == 1:
            print("arg1 : teams file")
            print("arg2 : topics file")
            print("arg3 : options [--only-group-number]")

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


        # Open teams description file
        with open(teams_filename) as file:
            self.teams = yaml.load(file, Loader=yaml.FullLoader)


        # Open topics description file
        with open(topics_filename) as file:
            topics = yaml.load(file, Loader=yaml.FullLoader)

            tree = []
            tree.append( list(topics.keys())[0] )
            k = topics 
            sujet_found = False

            while (sujet_found == False):
                if "Sujet_" in list(k[tree[-1]].keys())[0]:
                    sujet_found = True
                else:
                    kk = k
                    tree.append( list(k[tree[-1]].keys())[0] )
                    k = kk[tree[-2]]
            
            #print( tree )
            path_list = list(map(lambda x: x.lower().replace(' ',''), tree))
            #print (path_list)
            path = "/".join(path_list)        
            print( path )    

            #print( dict(k[tree[-1]].items()) )



        # attributes of the class set by this method :
        #
        # - Gitlab attribute gl
        self.gl = gitlab.Gitlab('https://gitlab.com', private_token=self.token)

        # - List of subgroups names
        self.project_subgrps_names = tree

        # - List of subgroups slugs
        self.project_subgrps_slugs = path_list

        # - String containing the path of the project
        self.project_url = path

        # - Topics dictionnary
        self.topics = dict(k[tree[-1]].items())

        # - Init lists
        self.topic_group_name = []
        self.topic_description = []
        #
        # --------------------------------------------







    def create_main_path(self):
        """
        Creates the path (chained subgroups) to the list of topics
        """    
        # Check first folder exist (Can't be created by API anyway)
        grps = self.gl.groups.list(search=self.project_subgrps_names[0])
        self.main_glgroup = None
        for i, grp in enumerate(grps):
            if grp.web_url == 'https://gitlab.com/groups/' + self.project_subgrps_slugs[0]:
                #print( grp )   
                self.main_glgroup = grp

        if self.main_glgroup == None:
            raise AssertionError("Le 'Group' racine dans GitLab est inexistant et doit être créé à la main")   
            
        #print( "\n" ) 
        
        group_n = self.gl.groups.get(self.main_glgroup.id, lazy=True)
        group_n_1 = group_n
        group_nl = group_n.subgroups.list()

        indice = 0

        while grp.web_url != ('https://gitlab.com/groups/' + self.project_url) :

            sgrp_exist = False

            if indice < len(self.project_subgrps_names) - 1 :
                indice = indice + 1
            else:
                break

            for i, grp in enumerate(group_nl):
                if grp.web_url in ('https://gitlab.com/groups/' + self.project_url) :
                    group_n_1 = copy.deepcopy(group_n)
                    group_n = self.gl.groups.get(grp.id, lazy=True)
                    group_nl = group_n.subgroups.list()
                    sgrp_exist = True
                    break

            

            if sgrp_exist == False:
                group_n_1 = copy.deepcopy(group_n)
                sub_group_id = self.gl.groups.create({'name': self.project_subgrps_names[indice], 'path': self.project_subgrps_slugs[indice], 'parent_id' : group_n_1.id } ).id
                group_n_1 = copy.deepcopy(group_n)
                group_n = self.gl.groups.get(sub_group_id, lazy=True)
                group_nl = group_n.subgroups.list()

        self.working_group = copy.deepcopy(group_n)

        return group_n
    


    def create_topics(self):
        """
        Creates a subgroup for each topic
        """  

        for topic_key, params in self.topics.items():

            self.topic_group_name.append( topic_key+'__'+params["name"].replace(' ','_')) 
            self.topic_description.append( '[' + params["description"] + '](' + params["url"] + ')'  )


        for i, topic_key in enumerate(self.topics):
            try:
                sub_group = self.gl.groups.create({'name': self.topic_group_name[i], 'path': self.topic_group_name[i], 'parent_id' : self.working_group.id } )
                print("{name} : created !".format(name = self.topic_group_name[i]))
            except:
                print("{name} : already existing".format(name = self.topic_group_name[i]))             

        print("\n")



    def create_projects(self, option=""):
        """
        Creates a project for each student group, and associate the right users to each project
        """  

        teams = self.teams 

        # sort_teams = yaml.dump(teams, sort_keys=True)

        print(teams)

        for topic_item, self.topic_content in teams.items():


            group_nl = self.working_group.subgroups.list(search=topic_item)
            for i, grp in enumerate(group_nl):
                if topic_item in grp.name:
                    break

            

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

                try:
                    grp
                    project = self.gl.projects.create({'name': self.prj_name, 'namespace_id': grp.id, 'description':  self.topic_description[topic_idx-1] } )
                    print("{name} : created !".format(name = self.prj_name)) 
                except:
                    print("{name} : already existing".format(name = self.prj_name)) 


                # List projects in order to associate the right users to each project
                projects = self.gl.projects.list(search=self.prj_name, namespace_id=grp.id)
                project = projects[0]

                for person in self.team_content:
                    ids = self.gl.users.list(search=person[2])
                    
                    if len(ids) > 0:
                        for ido in ids:
                            if(ido.username == person[2]):
                                try:
                                    member = project.members.create({'user_id': ido.id , 'access_level': gitlab.MAINTAINER_ACCESS})
                                    print("'- {member} : Member added to the project !".format(member = ido.username))
                                except:
                                    print("'- {member} : Member already exists".format(member = ido.username))
                                break                


if __name__ == "__main__":
    pg = ProjectsGenerator()

    pg.loadings()
    pg.create_main_path()
    pg.create_topics()
    pg.create_projects()

