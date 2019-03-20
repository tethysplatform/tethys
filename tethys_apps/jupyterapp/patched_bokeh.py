from bokeh.server.connection import ServerConnection


class PatchedServerConnection(ServerConnection):

    async def send_patch_document(self, event):
        """ Sends a PATCH-DOC message, returning a Future that's completed when it's written out. """
        msg = self.protocol.create('PATCH-DOC', [event])
        await self._socket._send_bokeh_message(msg)
