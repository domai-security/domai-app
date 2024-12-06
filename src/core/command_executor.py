... [previous content remains the same] ...

    async def _process_output(self,
                            command_id: str,
                            process: asyncio.subprocess.Process,
                            template: SecurityCommand) -> AsyncGenerator[Tuple[StreamOutput, StreamOutput], None]:
        """Process command output and generate dual-stream analysis"""
        try:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                output = line.decode().strip()
                if not output:
                    continue

                # Generate dual-stream analysis of output
                event = {
                    'type': command_id.split('_')[0],
                    'details': output,
                    'timestamp': datetime.now().isoformat(),
                    'command': template.command
                }

                crisis, knowledge = await self.stream_manager.process_security_event(event)
                yield crisis, knowledge

        except Exception as e:
            logging.error(f"Error processing output: {str(e)}")
            yield self.stream_manager._get_fallback_outputs()

    def stop_command(self, command_id: str):
        """Stop running command"""
        if command_id in self.active_processes:
            process = self.active_processes[command_id]
            process.terminate()
            del self.active_processes[command_id]
