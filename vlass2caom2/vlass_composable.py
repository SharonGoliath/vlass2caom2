# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2018.                            (c) 2018.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
#  $Revision: 4 $
#
# ***********************************************************************
#

import logging
import traceback

from vlass2caom2 import VlassArgsPassThrough, VlassNameHandler
from management import CaomExecute, Config


__all__ = ['Vlass2Caom2Meta', 'run_by_file']


class Vlass2Caom2Meta(CaomExecute):
    """Defines the pipeline step for VLASS ingestion of metadata into CAOM2.
    This requires access to only header information."""

    def __init__(self, config, obs_id):
        super(Vlass2Caom2Meta, self).__init__(VlassNameHandler, config, obs_id)
        self.pass_through = VlassArgsPassThrough()

    def execute(self, context):
        self.logger.debug('Begin execute for {} Meta'.format(__name__))
        self.logger.debug('the steps:')
        self.logger.debug('make sure named credentials exist')
        self._check_credentials_exist()

        self.logger.debug('create the work space, if it does not exist')
        self._create_dir()

        self.logger.debug('remove the existing observation, if it exists, '
                          'because metadata generation is less repeatable '
                          'for updates than for creates.')
        self._repo_cmd_delete()

        self.logger.debug('generate the xml, as the main_app will retrieve '
                          'the headers')
        artifact_uri = self.name_handler.get_file_uri()
        kwargs = {'params': {
            'observation': self.name_handler.get_obs_id(),
            'out_obs_xml': self.model_fqn,
            'collection': self.collection,
            'netrc': self.netrc_fqn,
            'artifact_uri': artifact_uri,
            'debug': True}}
        self.pass_through.collection_execute_augment(**kwargs)

        self.logger.debug('store the xml')
        self._repo_cmd('create')

        self.logger.debug('clean up the workspace')
        self._cleanup()

        self.logger.debug('End execute for {}'.format(__name__))


# class Vlass2Caom2Data(CaomExecute):
#     """Defines the pipeline step for OMM generation and ingestion of footprints
#     and previews into CAOM2. These are all the operations that require
#     access to the file on disk, not just the header data. """
#
#     def __init__(self, config, obs_id):
#         super(Vlass2Caom2Data, self).__init__(config, obs_id)
#
#     def execute(self, context):
#         self.logger.debug('Begin execute for {} Data'.format(__name__))
#         self.logger.debug('make sure named credentials exist')
#         self._check_credentials_exist()
#
#         self.logger.debug('create the work space, if it does not exist')
#         self._create_dir()
#
#         self.logger.debug('get the input file')
#         self._cadc_data_get()
#
#         self.logger.debug('get the observation for the existing model')
#         self._repo_cmd_read()
#         observation = self._read_model()
#
#         self.logger.debug('generate the previews')
#         self._generate_previews(observation)
#
#         self.logger.debug('generate the footprint')
#         self._generate_footprint(observation)
#
#         self.logger.debug('output the updated xml')
#         self._write_model(observation)
#
#         self.logger.debug('store the updated xml')
#         self._repo_cmd('update')
#
#         self.logger.debug('clean up the workspace')
#         self._cleanup()
#
#         self.logger.debug('End execute for {}'.format(__name__))
#
#     def _generate_previews(self, observation):
#         kwargs = {'working_directory': self.working_dir,
#                   'netrc_fqn': self.netrc_fqn}
#         omm_preview_augmentation.visit(observation, **kwargs)
#
#     def _generate_footprint(self, observation):
#         kwargs = {'working_directory': self.working_dir,
#                   'science_file': self.fname}
#         omm_footprint_augmentation.visit(observation, **kwargs)
#
#     def _read_model(self):
#         reader = obs_reader_writer.ObservationReader(False)
#         observation = reader.read(self.model_fqn)
#         return observation
#
#     def _write_model(self, observation):
#         writer = obs_reader_writer.ObservationWriter()
#         writer.write(observation, self.model_fqn)
#
#     def _cadc_data_get(self):
#         """Retrieve a collection file, even if it already exists. This might
#         ensure that the latest version of the file is retrieved from
#         storage."""
#         fqn = os.path.join(self.working_dir, self.fname)
#         data_cmd = 'cadc-data get -z --netrc {} {} {} -o {}'.format(
#             self.netrc_fqn, self.collection, self.obs_id, fqn)
#         manage_composable.exec_cmd(data_cmd)
#         if not os.path.exists(fqn):
#             raise manage_composable.CadcException(
#                 'Did not retrieve {}'.format(fqn))


def run_by_file():
    try:
        config = Config()
        config.get_executors()
        config.collection = 'VLASS'
        logger = logging.getLogger()
        logger.setLevel(config.logging_level)
        with open(config.work_fqn) as f:
            for line in f:
                obs_id = line.strip()
                logging.info('Process {}'.format(obs_id))
                meta = Vlass2Caom2Meta(config, obs_id)
                meta.execute(context=None)
                # data = Omm2Caom2Data(config, obs_id)
                # data.execute(context=None)
    except Exception as e:
        logging.error(e)
        tb = traceback.format_exc()
        logging.error(tb)
